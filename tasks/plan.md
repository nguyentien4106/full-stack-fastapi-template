# Implementation Plan: Free-Quota + Per-Page Billing (BankRow2Excel)

## Context

Today BankRow2Excel meters usage with a **prepaid VND balance** (`UserBalance`) topped up
via VNPAY, and tracks **lifetime** pages in `UserStorageStat.total_pages`. The product needs
a **monthly free quota**: the first **50 pages each calendar month are free**, and pages
beyond that cost **500 VND each**, deducted from the prepaid balance. There is no per-month
usage counter and no charging step today, so a new billing layer is required.

Decisions locked in `SPEC.md` (Resolved Decisions) and during planning:
- Price **500 VND/page**; free **50 pages/month**; reset at **start of calendar month**, Asia/Ho_Chi_Minh.
- A "page" = OCR `total_pages`. Charge happens **at OCR completion** (pages known then).
- **Failed jobs**: not billed, no quota consumption.
- **Insufficient balance at completion**: charge what the user has (floor at 0) and **deliver results**.
- **Upload-time pre-flight**: estimate pages from the PDF and **reject the upload (402)** if the
  estimated overage clearly exceeds balance + remaining free quota — saving wasted external OCR spend.

Intended outcome: every processed page is metered against a monthly free allowance, overage is
billed to the VND balance exactly once per job, and users are blocked up-front from jobs they
clearly cannot afford.

## Where this hooks into existing code

- **Completion hook (the one place pages become known):** `app/ocrs/service.py:get_ocr_job_status`,
  `state == OcrJobStatus.DONE` branch → already calls `upload_ocr_job_result()` which calls
  `increment_storage_stat(..., total_pages_delta=...)`. Billing attaches here.
- **Upload entry point:** `app/files/router.py:upload_file_endpoint` (before `post_ocr_jobs`).
- **Reusable as-is:** `app/topup/service.py:deduct_balance` (DEBIT txn + balance change, atomic),
  `app/topup/crud.py:get_or_create_balance`, `app/topup/crud.py:create_transaction`.
- **Conventions:** per-domain module layout (`models/schemas/crud/service/router/constants/exceptions`),
  SQLModel tables with explicit `__tablename__`, UUID PKs, `get_datetime_utc`, keyword-only service args,
  `HTTPException` with explicit codes, no `print` (ruff T201), mypy strict.

## Architecture Decisions

- **New `app/billing/` domain module** holds the quota/charging logic (constants, `MonthlyUsage`
  model, crud, service, exceptions). Keeps billing concerns out of `ocrs`/`files`.
- **`MonthlyUsage(user_id, year_month, pages_used)`**, unique on `(user_id, year_month)`, is the
  monthly source of truth. `year_month` is an `int` like `202606`, computed in Asia/Ho_Chi_Minh.
- **`FileJob.billed_at: datetime | None`** (new nullable column) is the idempotency guard — a job
  is billed at most once even under concurrent polling.
- **Charge math is a pure function** (`compute_chargeable_pages`) so quota boundaries are unit-tested
  without a DB or network.
- Reuse the existing balance/transaction primitives rather than writing new balance mutation code.

---

## Task List

### Phase 1 — Billing foundation (isolated, unit-tested)

#### Task 1: `MonthlyUsage` model + `FileJob.billed_at` + migration
**Description:** Create the `app/billing/` module with the `MonthlyUsage` table and add a nullable
`billed_at` column to `FileJob`. Generate one Alembic migration for both.
**Acceptance criteria:**
- [ ] `app/billing/models.py` defines `MonthlyUsage` (UUID PK, `user_id` FK→users CASCADE,
      `year_month: int` indexed, `pages_used: int = 0 ge=0`, `updated_at`), unique `(user_id, year_month)`.
- [ ] `FileJob` gains `billed_at: datetime | None` (tz-aware, default `None`).
- [ ] Both models re-exported from `app/models.py` shim so Alembic autogenerate sees them.
**Verification:**
- [ ] `alembic revision --autogenerate -m "add monthly_usage and filejob.billed_at"` produces a
      migration creating `monthly_usage` + adding `file_jobs.billed_at`.
- [ ] `alembic upgrade head` succeeds; `bash scripts/lint.sh` passes (mypy strict).
**Dependencies:** None
**Files:** `app/billing/__init__.py`, `app/billing/models.py`, `app/files/models.py`,
`app/models.py`, `app/alembic/versions/<new>.py`
**Scope:** S

#### Task 2: Quota constants + pure charge math
**Description:** Add billing constants and the pure functions that compute the current month key
and chargeable pages. No DB, no I/O.
**Acceptance criteria:**
- [ ] `app/billing/constants.py`: `FREE_PAGES_PER_MONTH = 50`, `PRICE_PER_PAGE_VND = 500`, tz `Asia/Ho_Chi_Minh`.
- [ ] `current_year_month()` returns the VN-timezone `YYYYMM` int.
- [ ] `compute_chargeable_pages(pages_used_this_month, job_pages)` = `max(0, used + job - 50)`.
- [ ] `chargeable_cost_vnd(chargeable_pages)` = `chargeable_pages * 500`.
**Verification:**
- [ ] `pytest tests/billing/test_quota_math.py -q` covers the boundary: used=49 + job=1 → 0 chargeable;
      used=49 + job=2 → 1; used=50 + job=3 → 3; used=0 + job=50 → 0; used=0 + job=51 → 1.
**Dependencies:** None
**Files:** `app/billing/constants.py`, `app/billing/service.py` (or `utils.py`), `tests/billing/test_quota_math.py`
**Scope:** S

#### Task 3: Billing service — `charge_for_job` (idempotent, partial-charge)
**Description:** Implement the service that charges a completed job once: reads month usage,
computes chargeable pages, deducts `min(cost, balance)` from the VND balance, increments
`MonthlyUsage.pages_used` by the job's pages, and stamps `FileJob.billed_at`. No-op if already billed.
**Acceptance criteria:**
- [ ] `app/billing/crud.py`: `get_or_create_monthly_usage`, `increment_monthly_usage`.
- [ ] `charge_for_job(session, *, user, file_job)`:
      returns early if `file_job.billed_at` is set or `total_pages` falsy;
      computes chargeable via Task 2; `amount = min(chargeable_cost, balance.balance)`;
      deducts via existing `deduct_balance`-style path (DEBIT txn `note`/`txn_ref` referencing job);
      increments monthly usage by `total_pages`; sets `billed_at`; commits atomically.
- [ ] Charging is **idempotent** (second call is a no-op) and never charges more than the balance.
**Verification:**
- [ ] `pytest tests/billing/test_charge_for_job.py -q`: (a) free-only job → no debit txn, usage +pages,
      billed_at set; (b) overage with sufficient balance → debit = pages*500, balance reduced;
      (c) overage exceeding balance → debit = full balance, balance floored at 0, results still proceed;
      (d) calling twice charges once.
**Dependencies:** Tasks 1, 2
**Files:** `app/billing/crud.py`, `app/billing/service.py`, `app/billing/exceptions.py`,
`tests/billing/test_charge_for_job.py`
**Scope:** M

### Checkpoint: Foundation
- [ ] `bash scripts/test.sh` green; `bash scripts/lint.sh` clean.
- [ ] Billing math + charging proven in isolation, no live wiring yet. **Review with human.**

---

### Phase 2 — Wire into the live parse flow

#### Task 4: Charge at OCR completion
**Description:** Invoke `charge_for_job` at the `DONE` transition so a job is metered+billed the
moment pages are known. Keep `increment_storage_stat` (lifetime) as-is.
**Acceptance criteria:**
- [ ] In `app/ocrs/service.py` (DONE branch / `upload_ocr_job_result`), call
      `charge_for_job(session, user=user, file_job=file_job)` after the job is marked `DONE` and
      `total_pages` is persisted.
- [ ] `FAILED` jobs are never charged; re-polling a `DONE` job does not double-charge (billed_at guard).
**Verification:**
- [ ] `pytest tests/billing/test_completion_charge.py -q` with the OCR HTTP call mocked: a job
      transitioning to DONE deducts the expected VND and increments `MonthlyUsage`; a second poll is a no-op;
      a FAILED job leaves balance/usage untouched.
**Dependencies:** Task 3
**Files:** `app/ocrs/service.py`, `tests/billing/test_completion_charge.py`
**Scope:** S

#### Task 5: Upload-time pre-flight page estimate + 402 block
**Description:** Before submitting to OCR, estimate the PDF's page count and reject the upload when
the estimated overage clearly can't be covered, saving external OCR cost.
**Acceptance criteria:**
- [ ] Add `pypdf` dependency (**ask-first item — confirm at implementation**).
- [ ] `app/billing/service.py:estimate_pdf_pages(data: bytes) -> int | None` (None when not a PDF/uncountable).
- [ ] In `upload_file_endpoint`, before `post_ocr_jobs`: if pages estimable, compute estimated
      chargeable cost vs `balance`; if `estimated_cost > balance`, delete the staged `File` and raise
      **HTTP 402** with a "top up to continue" message (and the estimated cost). Non-PDF / uncountable
      uploads skip the block and rely on completion-time charging.
**Verification:**
- [ ] `pytest tests/api/routes/test_files_billing.py -q`: upload of an N-page PDF by a user with
      insufficient balance → 402 and no OCR job submitted (mock `post_ocr_jobs`); sufficient balance → proceeds.
**Dependencies:** Tasks 2, 3
**Files:** `app/files/router.py`, `app/billing/service.py`, `pyproject.toml`,
`tests/api/routes/test_files_billing.py`
**Scope:** M

### Checkpoint: Core flow
- [ ] End-to-end (mocked externals): upload → OCR done → balance/quota updated correctly; over-budget
      uploads blocked. `bash scripts/test.sh` green. **Review with human.**

---

### Phase 3 — Surface usage + front-end

#### Task 6: Usage/quota API endpoint
**Description:** Expose what the UI needs: remaining free pages this month, pages used, balance, price.
**Acceptance criteria:**
- [ ] `GET /billing/usage` (new `app/billing/router.py`, registered in `app/api/main.py`) returns
      `{ year_month, pages_used, free_pages_remaining, price_per_page_vnd, balance_vnd }` for the current user.
- [ ] Endpoint enforces auth (`CurrentUser`).
**Verification:**
- [ ] `pytest tests/api/routes/test_billing_usage.py -q`: a user mid-month sees correct
      `free_pages_remaining = max(0, 50 - pages_used)` and balance.
**Dependencies:** Tasks 1, 3
**Files:** `app/billing/router.py`, `app/billing/schemas.py`, `app/api/main.py`,
`tests/api/routes/test_billing_usage.py`
**Scope:** S

#### Task 7: Front-end — show quota + handle 402
**Description:** Surface remaining free pages + balance, and turn the upload 402 into a clear
"top up to continue" message. (FE testing stays typecheck/lint only per spec.)
**Acceptance criteria:**
- [ ] Regenerate SDK: `bun run generate-client` after the new endpoints exist.
- [ ] Dashboard shows free-pages-remaining + balance from `GET /billing/usage`.
- [ ] Upload flow catches **402** and shows the top-up prompt (i18n strings in `messages/en.json` + `vi.json`).
**Verification:**
- [ ] `bun run typecheck` and `bun run lint` pass. Manual: as a low-balance user, an over-budget
      upload shows the top-up prompt; usage widget reflects pages used after a successful parse.
**Dependencies:** Task 6
**Files:** `front-end/lib/client/*` (generated), a dashboard component, upload action/component,
`front-end/messages/en.json`, `front-end/messages/vi.json`
**Scope:** M

### Checkpoint: Complete
- [ ] All `SPEC.md` Success Criteria met; backend `bash scripts/test.sh` + `bash scripts/lint.sh` green;
      FE `bun run typecheck`/`lint` green. **Final review with human.**

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Concurrent status-polls double-charge a job | High | `FileJob.billed_at` guard checked inside `charge_for_job`; charge in the same committed transaction |
| `pypdf` estimate ≠ OCR `total_pages` | Med | Estimate only gates the up-front block; the authoritative charge uses `total_pages` at completion; "charge what they have" absorbs small shortfalls |
| Month boundary / timezone off-by-one | Med | Single `current_year_month()` helper pinned to Asia/Ho_Chi_Minh; unit-test boundary |
| Adding `pypdf` dependency | Low | Flagged ask-first in Task 5 before install |
| Charge happens inside OCR polling path (latency/errors) | Med | Billing failure must not corrupt job state — wrap so a charge error is logged and retried on next poll, not lost (billed_at only set on success) |

## Out of scope (follow-ups, not blocking)

- Scheduled removal of legacy `frontend/` and the template `items/` domain (SPEC decision #7) — separate cleanup task.
- Subscription/auto-recharge; refunds for failed exports.

## Verification (end-to-end)

1. `cd backend && alembic upgrade head` then `bash scripts/test.sh` — all billing tests green.
2. Run `fastapi dev app/main.py`; with a seeded user at balance 0 and 0 pages used, upload a
   small PDF (≤50 pages) → completes, `GET /billing/usage` shows pages_used>0, balance unchanged.
3. Push monthly usage to 50, upload another PDF with balance 0 → **402** at upload.
4. Top up via balance, upload again → completes; balance reduced by `overage_pages * 500`.
5. Re-poll `GET /files/{id}/status` on a done job → balance unchanged (idempotent).
6. FE: `bun run typecheck` + `bun run lint` pass; usage widget + 402 prompt verified manually.

## Note on file locations

Per the `/plan` request, on approval this plan will be copied to `tasks/plan.md` and the task
checklist to `tasks/todo.md` (plan mode only permits editing this plan file for now).
