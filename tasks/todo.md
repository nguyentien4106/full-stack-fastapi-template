# TODO: Free-Quota + Per-Page Billing

Full plan: [tasks/plan.md](plan.md) · Spec: [SPEC.md](../SPEC.md)

Rules: 50 free pages/month (calendar month, Asia/Ho_Chi_Minh) · 500 VND/page overage ·
page = OCR `total_pages` · charge at OCR completion · failed jobs free · charge what they
have & deliver on shortfall · upload-time `pypdf` pre-flight 402 block.

## Phase 1 — Billing foundation
- [x] **Task 1 (S):** `MonthlyUsage` model + `FileJob.billed_at` column + Alembic migration ✅ (commit ab5e3a9)
  - Files: `app/billing/{__init__,models}.py`, `app/files/models.py`, `app/models.py`, `app/alembic/versions/c2d3e4f5a6b7_*.py`
  - Verify: `alembic upgrade head` ✅; `pytest tests/billing/test_models.py` ✅; ruff ✅
  - Note: `mypy` is pre-existing-broken repo-wide (SQLModel `sa_type` overload); new code matches `# ty:ignore` convention
- [ ] **Task 2 (S):** Quota constants + pure charge math (`current_year_month`, `compute_chargeable_pages`, `chargeable_cost_vnd`)
  - Files: `app/billing/constants.py`, `app/billing/service.py`, `tests/billing/test_quota_math.py`
  - Verify: `pytest tests/billing/test_quota_math.py -q` (boundary 49+1→0, 49+2→1, 0+51→1)
- [ ] **Task 3 (M):** `charge_for_job` — idempotent, partial-charge, increments monthly usage, stamps `billed_at`
  - Files: `app/billing/{crud,service,exceptions}.py`, `tests/billing/test_charge_for_job.py`
  - Verify: `pytest tests/billing/test_charge_for_job.py -q` (free / overage / shortfall / double-call)
- [ ] **Checkpoint:** `bash scripts/test.sh` + `bash scripts/lint.sh` green — review with human

## Phase 2 — Wire into live flow
- [ ] **Task 4 (S):** Call `charge_for_job` at OCR `DONE` transition (`app/ocrs/service.py`)
  - Verify: `pytest tests/billing/test_completion_charge.py -q` (charges once, FAILED untouched)
- [ ] **Task 5 (M):** Upload pre-flight — `estimate_pdf_pages` (add `pypdf`, ask-first) + 402 block in `upload_file_endpoint`
  - Files: `app/files/router.py`, `app/billing/service.py`, `pyproject.toml`, `tests/api/routes/test_files_billing.py`
  - Verify: `pytest tests/api/routes/test_files_billing.py -q` (insufficient → 402, no OCR submit)
- [ ] **Checkpoint:** end-to-end mocked flow green; over-budget uploads blocked — review with human

## Phase 3 — Surface usage + front-end
- [ ] **Task 6 (S):** `GET /billing/usage` endpoint (`app/billing/{router,schemas}.py`, register in `app/api/main.py`)
  - Verify: `pytest tests/api/routes/test_billing_usage.py -q`
- [ ] **Task 7 (M):** FE — `bun run generate-client`, quota widget, 402 handling, i18n strings (en/vi)
  - Verify: `bun run typecheck` + `bun run lint`; manual over-budget upload prompt
- [ ] **Checkpoint:** all SPEC success criteria met; backend + FE checks green — final review

## Follow-ups (out of scope)
- [ ] Remove legacy `frontend/` + template `items/` domain (SPEC decision #7)
