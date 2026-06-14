# Spec: BankRow2Excel — Bank Statement → Excel Parser

> **Status:** Canonical spec for the existing system + the new free-quota billing layer.
> **Last updated:** 2026-06-14
> Sections tagged **[EXISTS]** document already-built behavior (source of truth going
> forward). Sections tagged **[NEW]** are not yet implemented and define work to do.

---

## Objective

**What:** A web application that lets accountants turn bank-statement documents (PDF)
into a structured Excel file of transactions, where each transaction is automatically
classified into a Vietnamese accounting account code (mã tài khoản kế toán, per
Thông tư 200/2014/TT-BTC).

**Who:** Accountants in the Vietnamese market who today re-key bank-statement
transactions into accounting software by hand.

**Why:** Manual transcription of statement lines and assigning account codes is slow
and error-prone. Automating OCR + classification turns a multi-hour task into a
single upload-and-download.

**Success looks like:** A signed-in accountant uploads a bank-statement PDF, the system
extracts every transaction, assigns a best-guess accounting account code (leaving it
blank when uncertain), and returns a downloadable `.xlsx`. Usage is metered by pages:
the first 50 pages each month are free, and additional pages are charged against the
user's prepaid VND balance.

### User stories / acceptance criteria

- As a visitor, I can **sign up and sign in** so I have an account and usage history.
- As a signed-in user, I can **upload a bank-statement PDF** and see a parsing job
  progress through `pending → running → done/failed`.
- As a signed-in user, I can **preview the extracted transaction table** in the browser
  before downloading.
- As a signed-in user, I can **download the result** as `.xlsx` (and `.csv`/`.json`/`.html`),
  including the assigned account-code columns.
- As a signed-in user, my **first 50 pages each calendar month are free**; beyond that,
  each page is deducted from my **prepaid VND balance**. **[NEW]**
- As a signed-in user, I can **top up my VND balance via VNPAY** when I run low.
- As a signed-in user, I am **blocked from starting a job** that would exceed both my
  free quota and my available balance, with a clear message to top up. **[NEW]**

---

## Tech Stack

**Backend** (`backend/`)
- Python ≥3.10, **FastAPI** (`fastapi[standard]`), **SQLModel** over PostgreSQL
- **Alembic** migrations
- **Pydantic v2** + `pydantic-settings`
- Auth: JWT (`pyjwt`), password hashing via `pwdlib[argon2,bcrypt]`
- OCR: external **PaddleOCR** API (PaddleOCR-VL / PP-OCRv5/v6 / PP-StructureV3)
- Classification: **Google Gemini** (`google-genai`, model `gemini-3-flash-preview`)
- Tabular processing/export: `pandas` + `openpyxl`
- Object storage: **Cloudflare R2** via `boto3` (`app/aws/`)
- Payments: **VNPAY** (`app/vnpay/`)
- Monitoring: `sentry-sdk[fastapi]`
- Tooling: `pytest`, `coverage`, `mypy` (strict), `ruff`, `prek` (pre-commit)

**Front-end** (`front-end/`)
- **Next.js 14** (App Router), TypeScript, **bun** only (no npm/node on PATH)
- `next-intl` (en/vi, `/en` `/vi` prefixes), `next-themes`, Tailwind v3, `lucide-react`,
  `recharts`, `framer-motion`
- API client generated from backend OpenAPI via **`@hey-api/openapi-ts`** (`lib/client/`)
- Branded **BankRow2Excel**; auth cookie `bankrow2excel_token`
- Config file must be `next.config.mjs` (Next 14 rejects `.ts`)

> There is also a legacy Vite app in `frontend/` (lowercase). `front-end/` (hyphen) is
> the active Next.js front-end.

---

## Commands

**Backend** (run from `backend/`)
```
Install:   uv sync
Dev:       fastapi dev app/main.py            # or: uvicorn app.main:app --reload
Migrate:   alembic upgrade head
New migration: alembic revision --autogenerate -m "<message>"
Lint:      bash scripts/lint.sh               # ruff check + mypy strict
Format:    bash scripts/format.sh             # ruff format + ruff check --fix
Test:      bash scripts/test.sh               # coverage run -m pytest + html report
Test (one): pytest tests/api/routes/test_login.py -q
Prestart:  bash scripts/prestart.sh           # migrations + initial data
```

**Front-end** (run from `front-end/`, bun only)
```
Install:   bun install
Dev:       bun run dev                        # next dev, port 3000
Build:     bun run build                      # next build
Start:     bun run start
Lint:      bun run lint                       # next lint
Typecheck: bun run typecheck                  # tsc --noEmit  (or: bunx tsc --noEmit)
Gen client: bun run generate-client           # regenerate SDK from openapi.json
```

**Stack (containers)**
```
docker compose up -d                          # see compose.yml / compose.override.yml
```

---

## Project Structure

```
backend/
  app/
    main.py              → FastAPI app, CORS, Sentry, router include
    api/main.py          → aggregates all domain routers under /api/v1
    core/                → config (settings), db engine, security (JWT/hashing)
    auth/                → login, token, password reset
    users/               → user CRUD, registration, profile
    files/               → File + FileJob models, upload, parse, preview, export  ← core domain
    ocrs/                → PaddleOCR job submission + status polling
    aws/                 → Cloudflare R2 client (upload/download)
    topup/               → UserBalance + TopupTransaction (VND balance, packages)
    vnpay/               → VNPAY payment client + callback handling
    storages/            → UserStorageStat (per-user file/page/cost usage)
    api_keys/            → per-user API keys
    items/               → template demo domain (from FastAPI template; may be removed)
    models.py            → backwards-compat shim re-exporting per-domain models
  tests/
    api/routes/          → endpoint tests
    crud/                → CRUD-level tests
    utils/               → test fixtures/helpers
  scripts/               → lint.sh, format.sh, test.sh, prestart.sh
  alembic.ini, app/alembic/ → migrations

front-end/
  app/[locale]/          → i18n routes; (app) route group has role-aware dashboard
  components/            → UI components
  lib/                   → api.ts, auth.ts, actions.ts, files.ts, client/ (generated SDK)
  messages/              → en/vi i18n strings
  middleware.ts          → next-intl + auth middleware
```

**Each backend domain module follows the same layout:**
`models.py` (table models) · `schemas.py` (request/response) · `crud.py` (DB access) ·
`service.py` (business logic) · `router.py` (endpoints) · `dependencies.py` ·
`constants.py` · `exceptions.py`.

---

## Core Domain Flow (parse pipeline) **[EXISTS]**

1. **Upload** — client POSTs a PDF; backend stores the original in **Cloudflare R2**
   and creates a `File` row (`filename`, `content_type`, `size`, `url`, `bank`, `user_id`).
2. **OCR** — backend submits the file to the external **PaddleOCR** API
   (`app/ocrs/service.py: post_ocr_jobs`), creating a `FileJob` with `state=pending`.
   Status is polled (`get_ocr_job_status`); on completion the job stores `json_url` /
   `markdown_url`, `total_pages`, `extracted_pages`, and `state=done`.
3. **Classify** — `POST /files/{file_id}/download/ai` runs the parsed table through
   **Gemini** with a Vietnamese instruction that assigns each transaction an accounting
   account code + name (Thông tư 200/2014/TT-BTC). **When the transaction content is
   not certain, the code is left blank.**
4. **Export** — `download_file()` uses a `DownloadStrategy` (`app/files/strategies.py`)
   to convert the result DataFrame to `xlsx` (default), `csv`, `json`, or `html`.
5. **Preview** — `get_preview_data()` returns the same table inline as `(columns, rows)`
   for in-browser display.

Job states: `pending | running | done | failed` (`app/ocrs/constants.py: OcrJobStatus`).

---

## Billing & Metering **[NEW — primary new work]**

Today billing is a **prepaid VND balance** (`UserBalance`) topped up via **VNPAY**
(`TopupTransaction`, packages 20k–10M VND in `app/topup/constants.py`). Per-user usage
is already tracked in `UserStorageStat` (`total_pages`, `total_transactions`, `total_cost`).

The new metering layer adds a **monthly free quota**:

- **Free quota:** each user gets **50 free pages per calendar month**, reset at the
  **start of each calendar month** (Asia/Ho_Chi_Minh timezone for "month" boundaries).
- **Overage price:** pages beyond the free 50 in a month are charged at **500 VND per page**,
  deducted from `UserBalance.balance`.
- **Metering unit:** **pages**, taken from the OCR job's `total_pages` (the authoritative
  page count, known once OCR completes).
- **Charge point:** billing runs **at OCR completion** (when `state=done` and `total_pages`
  is known) — not at download. A previewed-but-not-downloaded job is still billed.
- **Failed jobs are not billed** and their pages do **not** count against the free quota.
- **Pre-flight check:** before billing, compute
  `chargeable_pages = max(0, pages_used_this_month + job_pages - 50)`.
  If `chargeable_pages * 500 > balance`, **block the job** and prompt the user to top up.
- **Charging is atomic & idempotent per job:** a page is billed at most once; record a
  `TopupTransaction` of `type=debit` referencing the job so re-runs don't double-charge.
- **Ordering:** free pages are consumed first within a month, then balance.

Required new pieces (high level — to be detailed in the Plan phase):
- A monthly-usage source of truth (e.g. `pages_used` per `(user_id, year_month)`), since
  `UserStorageStat.total_pages` is lifetime, not monthly.
- A billing service that runs at OCR-completion (when `total_pages` is known) and at
  the AI/export step, enforcing quota + balance and writing the debit transaction.
- API surface for the user to see remaining free pages and balance.

---

## Code Style

**Backend** — strict typed FastAPI + SQLModel, domain-module layout, Google-style
docstrings on services. `ruff` (E/W/F/I/B/C4/UP/ARG001/T201 — **no `print`**) and
`mypy --strict`.

```python
# app/<domain>/service.py
def charge_for_job(session: Session, *, user: User, job: FileJob) -> TopupTransaction | None:
    """Charge a user for an OCR job's pages, applying the monthly free quota first.

    The first 50 pages each month are free; pages beyond that are deducted from the
    user's prepaid VND balance. Returns the debit ``TopupTransaction`` when a charge was
    made, or ``None`` when the job fit entirely within the free quota. Raises
    ``InsufficientBalanceError`` when the balance cannot cover the chargeable pages.
    """
    pages = job.total_pages or 0
    chargeable = compute_chargeable_pages(session, user_id=user.id, job_pages=pages)
    if chargeable == 0:
        return None
    ...
```

Conventions:
- One table per file in `models.py`; `__tablename__` explicit; UUID PKs via
  `default_factory=uuid.uuid4`; timezone-aware datetimes via `get_datetime_utc`.
- Endpoints raise `HTTPException` with explicit status codes; enforce ownership
  (`if file.user_id != user.id: 403`) on every per-resource route.
- Keyword-only args for service functions (`*,`); domain exceptions in `exceptions.py`.

**Front-end** — TypeScript, Next.js App Router, server actions for auth in
`lib/actions.ts`; generated SDK for typed calls; `next-intl` for all user-facing strings
(no hardcoded copy — add to `messages/en.json` + `messages/vi.json`). Use markdown link
syntax for file refs in docs.

---

## Testing Strategy

- **Framework:** `pytest` + `coverage` (backend). Run via `bash scripts/test.sh`.
- **Location:** `backend/tests/` mirrors app structure — `tests/api/routes/` for endpoint
  tests, `tests/crud/` for DB-layer tests, `tests/utils/` for fixtures.
- **Levels:**
  - *Unit* — billing math (`compute_chargeable_pages`, quota reset boundaries),
    export strategies, Gemini-response parsing. Pure functions, no network.
  - *Integration* — endpoint tests against a test DB session (existing pattern in
    `tests/api/routes/`), with **external services (PaddleOCR, Gemini, VNPAY, R2) mocked**.
- **Coverage expectation:** new billing/quota logic must have unit tests for the quota
  boundary (49→50→51 pages), insufficient-balance block, and idempotent double-charge.
- **Front-end:** typecheck (`bun run typecheck`) + lint must pass; component/E2E testing
  is not yet established (*Open Question*).
- **Never** test by hitting real Gemini/VNPAY/PaddleOCR/R2 — always mock external calls.

---

## Boundaries

**Always do**
- Run `bash scripts/lint.sh` (ruff + mypy strict) and `bash scripts/test.sh` before commits.
- Enforce per-resource ownership checks (`user_id`) on every authenticated route.
- Add new user-facing strings to both `messages/en.json` and `messages/vi.json`.
- Mock external services (Gemini, PaddleOCR, VNPAY, R2) in tests.
- Regenerate the front-end SDK (`bun run generate-client`) after backend API changes.
- Keep money in VND as the stored balance unit; bill in whole pages.

**Ask first**
- Database schema changes / new Alembic migrations.
- Adding dependencies (backend `uv` or front-end `bun`).
- Changing the per-page price, free-quota size, or VNPAY package amounts.
- Changing the Gemini model or the Vietnamese classification prompt/account-code logic.
- Changing CORS, auth/token, or CI config.
- Removing the legacy `frontend/` or template `items/` domain.

**Never do**
- Commit secrets (Gemini/VNPAY/R2 keys, JWT secret) — they live in `.env`, not the repo.
- Double-charge a user for the same job's pages.
- Start a parsing job that would exceed quota + balance without an explicit block message.
- Use `print` in backend code (ruff `T201`) — use the logger.
- Remove or skip failing tests without approval.
- Switch the parsing engine away from Gemini, or drop VN account-code classification
  (both are core, confirmed product features).

---

## Success Criteria

- [ ] A new user can sign up, sign in, and upload a bank-statement PDF.
- [ ] A completed job exposes `total_pages` and a previewable transaction table.
- [ ] Downloaded `.xlsx` contains the transactions plus assigned account-code + name
      columns, with uncertain rows left blank.
- [ ] The first 50 pages in a calendar month incur **no** balance deduction. **[NEW]**
- [ ] Page 51+ in a month deducts `price_per_page` VND from `UserBalance`. **[NEW]**
- [ ] A job that cannot be covered by free quota + balance is blocked with a top-up prompt. **[NEW]**
- [ ] Re-running export/AI on the same job does **not** charge twice. **[NEW]**
- [ ] `bash scripts/lint.sh` and `bash scripts/test.sh` pass; new billing logic is unit-tested.

---

## Resolved Decisions

1. **Per-page overage price:** **500 VND per page** beyond the free 50/month.
2. **Quota reset:** at the **start of each calendar month** (Asia/Ho_Chi_Minh timezone).
3. **A "page"** = OCR `total_pages` (PDF pages).
4. **Charge point:** at **OCR completion** (when `total_pages` is known), not at download —
   a previewed-but-not-downloaded job is still billed.
5. **Failed jobs:** **not** billed, and their pages do **not** count against the free quota.
6. **Front-end testing:** stay **typecheck + lint only** (no Playwright/E2E for now).
7. **Legacy `frontend/` and template `items/` domain:** **scheduled for removal** (separate
   cleanup task — do not block the billing work on it).
```
