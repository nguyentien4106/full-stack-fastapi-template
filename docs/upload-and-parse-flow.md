## Upload & Parse Flow

Purpose
-------

This document describes a production-ready end-to-end flow for "user uploads a document → server persists file to R2 → OCR parsing runs (parallel) → client polls for result." It includes the sequence, API contracts, data shapes, orchestration, error handling, security, and examples.

High-level contract
-------------------
- Input: user-authenticated file upload (single file or multipart). Output: job id that can be polled for status and final parse result.
- Processing: file stored durably in R2, a Job + Document record created, parsing tasks submitted to workers/OCR provider in parallel, partial results persisted and aggregated.
- Success: final status = `completed` with parsed data and extracted metadata. Error modes: transient (retryable) vs permanent (manual intervention).
- Non-functional: idempotent uploads, rate-limited OCR calls, auditable operations, monitoring and alerts for failures.

Edge cases to handle
--------------------
- Very large files (large PDFs, many pages) → chunking or reject with guidance.
- Duplicate uploads (user retries) → idempotency via `client_upload_id` or checksum.
- OCR provider rate limits / outages → queue + backoff + DLQ.
- Partial parsing (some pages fail) → aggregated job-level status with per-page errors.
- PII / compliance: redact or restrict storage of sensitive fields when storing parsed text (policy).

Sequence overview
-----------------

1. Client POST `/upload` (or presigned PUT) with file + metadata.
2. Server stores file to R2 (or returns presigned URL to client for direct upload).
3. Server creates DB Job and Document metadata, enqueues parsing tasks (per-file or per-page).
4. Worker pool consumes tasks, calls external OCR API in parallel, stores ParseResult(s) to DB/R2.
5. Aggregation completes, Job status updated to `completed`/`failed`. Client polls `/jobs/{job_id}` or receives webhook.

Design choices & rationale
-------------------------
- Store original file in R2 (cheap, durable); keep references in DB (filename, size, checksum, R2 key).
- Prefer server-generated presigned PUT URLs for large uploads to avoid server memory pressure.
- Use a queue (Redis + RQ/Celery, or SQS) + worker pool to decouple ingestion from slow OCR API calls.
- Split work into smaller units (pages or chunks) for parallelism and better error isolation.
- Provide both polling and webhook options for clients; polling is simpler and robust for many clients.

API Contracts
-------------

1) Upload endpoint (server-mediated or presigned)

Option A — Server-handled upload (multipart)

- POST `/upload`
- Auth: Bearer JWT
- Request: `multipart/form-data` { file: file, metadata?: JSON, client_upload_id?: string }
- Response `202 Accepted`

```
{
  "job_id": "uuid",
  "document_id": "uuid",
  "status": "pending",
  "poll_url": "/jobs/{job_id}"
}
```

Option B — Presigned upload (recommended for large uploads)

- POST `/uploads/presign`
- Request JSON:

```
{ "filename": "file.pdf", "content_type": "application/pdf", "client_upload_id?": "string", "metadata?": { ... } }
```
- Response 200:

```
{
  "upload_url": "https://r2...signed-url",
  "file_key": "r2-key",
  "job_id": "uuid",
  "document_id": "uuid",
  "complete_upload_url": "/uploads/complete"
}
```
- Client: PUT file to `upload_url`. Then POST `/uploads/complete` { file_key, job_id } to signal server to start parsing.

2) Start/Complete upload (server)

- POST `/uploads/complete`
- Body: `{ job_id: "uuid", file_key: "string", checksum?: "sha256", metadata?: {} }`
- Response 200 -> same job_id.

3) Polling/Get job

- GET `/jobs/{job_id}`
- Auth: Bearer JWT (owners or admins)
- Response:

```
{
  "job_id":"uuid",
  "document_id":"uuid",
  "status":"pending|processing|partial|completed|failed",
  "created_at":"iso",
  "updated_at":"iso",
  "progress": { "total_tasks": 10, "completed_tasks": 7 },
  "results": [ { "page":1,"status":"completed","result_key":"r2-key-or-db-id" }, ... ],
  "error": { "message": "...", "code": "OCR_PROVIDER_429" }
}
```

4) Get parse result

- GET `/documents/{document_id}/result` or `/jobs/{job_id}/result`
- Support pagination for large parse outputs or per-page retrieval.

5) Webhook (optional)

- POST `/webhooks/parse-complete`
- Body: `{ job_id, document_id, status, summary: {...} }`
- Security: sign webhook (HMAC) or mutual TLS.

Data Models (conceptual)
------------------------
- Job
  - id uuid PK
  - user_id uuid FK
  - status enum
  - client_upload_id nullable string (idempotency)
  - created_at, updated_at
  - error JSON nullable
- Document
  - id uuid
  - job_id uuid
  - r2_key string
  - filename string
  - size int
  - checksum string
  - pages int nullable
- Task (optional — per-page)
  - id uuid
  - document_id
  - page_number int nullable
  - status enum
  - attempts int
  - last_error JSON
  - result_key string (link to parsed output in R2 or DB)
- ParseResult
  - id uuid
  - document_id
  - task_id
  - extracted_text (or link)
  - structured_data JSON
  - created_at

Storage conventions (R2)
-----------------------
- Bucket layout:
  - `originals/{year}/{month}/{job_id}/{document_id}/{filename}`
  - `results/{year}/{month}/{job_id}/{document_id}/page-{n}.json`
- Filenames: `{uuid}_{sanitized_name}` for traceability.
- Store checksums (sha256) & content-type.
- Lifecycle: set retention policy if needed; consider lifecycle rules to move older originals to cold storage.
- Signed URLs: presigned PUT for upload and presigned GET for downloads; short TTL (e.g., 15m).

OCR orchestration & parallel parsing
-----------------------------------
- Chunking:
  - For PDFs: extract pages server-side (if needed) and submit one task per page.
  - For images: per-file task.
- Worker pool:
  - Use a queue (Redis, SQS) and workers (Celery/RQ or managed pool).
  - Concurrency limits: set by OCR provider rate limits and CPU/memory costs.
  - Task flow: worker fetches task -> download file/page from R2 -> call OCR -> store result -> ack.
- Parallelism & rate limiting:
  - Workers implement a rate-limited client for OCR provider (token bucket).
  - For bursty loads, use a local queue and throttle to avoid exceeding external quotas.
- Idempotency:
  - Each task should have an idempotency key (job_id + document_id + page_number). If a ParseResult exists, skip reprocessing.
- Timeouts & retries:
  - Set a sensible timeout for OCR calls (e.g., 60s). Retry transient errors with exponential backoff (max 3-5 attempts). Permanent errors mark task failed and optionally send to DLQ.
- Aggregation:
  - A coordinator or the Job record tracks number of tasks vs completed tasks; when all tasks are completed/failed, compute job-level status.

Polling strategy
----------------
- Client receives `job_id` and `poll_url`.
- Poll frequency: start aggressive for a short time, then back off exponentially with cap. Example: 1s, 2s, 4s, 8s, 16s, 30s (cap).
- Include `ETag`/`Last-Modified` in responses to reduce payloads. Clients may use conditional requests.
- Provide webhook/SSE/websocket alternative for real-time needs.

Backoff and retry policy for client polling
-----------------------------------------
- Use exponential backoff with jitter to avoid thundering herd.
- If job age > threshold (e.g., 10 minutes), switch to polling every 30–60s and surface a message to the client that the job is long-running.

Error handling and retry policy (server)
---------------------------------------
- Error types:
  - Transient: OCR provider 429/5xx, network timeouts → retry with backoff.
  - Permanent: invalid file, unsupported format → mark task failed immediately.
- Retries:
  - For transient OCR errors: up to N attempts (3–5) with exponential backoff.
  - After all attempts fail: write to DLQ and mark task failed; notify via alert.
- Partial success:
  - If some pages succeed and others fail, return aggregated results and per-page error details.
- Audit:
  - Store full error payloads for debugging in DB or logs (mask PII).
- Circuit breaker:
  - If OCR provider returns many failures, temporarily stop making new calls and back off globally.

Security & compliance
---------------------
- Auth: Bearer JWT with scopes for upload and job read; verify user owns job/document.
- Signed URLs: presigned PUT/GET URLs with short expiry; restrict methods/headers.
- Input validation: validate content-types, enforce file size limits.
- Malware scanning: integrate virus scanning on upload (optional) before enqueueing.
- PII & encryption: encrypt at rest (R2 settings), TLS in transit; implement data retention and deletion policy.
- Audit logs: log who uploaded, processed, and accessed results.
- Webhook security: sign webhook payloads with HMAC secret.

Monitoring, metrics & alerts
---------------------------
- Metrics:
  - `job_created`, `job_completed`, `job_failed`, `average_job_time`, `queue_depth`, `worker_count`, `ocr_api_errors`, `ocr_api_throttles`.
- Logs:
  - Structured logs for each job/task including `job_id`.
- Alerts:
  - Alert on high queue depth, elevated failure rates, OCR provider downtime, or sudden latency spikes.
- Healthcheck endpoints for API and workers.

Data retention & deletion
------------------------
- Soft-delete documents (mark as deleted) with a scheduled job to purge after retention period.
- Offer user-initiated deletion that marks job/document and schedules removal from R2 and DB.
- When removing data, also remove parse results and event logs (or archive them as needed for compliance).

Data schemas / Example JSON
---------------------------

Upload response

```
{
  "job_id": "7b8e1a2e-....",
  "document_id": "a1234bcd-....",
  "status": "pending",
  "poll_url": "/jobs/7b8e1a2e-...."
}
```

Job status response

```
{
  "job_id":"7b8e1a2e-....",
  "status":"processing",
  "progress":{"total_tasks":10,"completed_tasks":6},
  "results":[
    {"page":1,"status":"completed","result_key":"results/.../page-1.json"},
    {"page":2,"status":"failed","error":{"code":"OCR_500","message":"timeout"}}
  ],
  "error":null
}
```

Parse result (per page)

```
{
  "document_id":"a1234bcd-....",
  "page":1,
  "text":"Extracted OCR text...",
  "entities":[ {"type":"date","value":"2026-01-23","span":[10,20]} ],
  "confidence":0.98
}
```

Example server-side pseudocode (Python / FastAPI + Celery style)
---------------------------------------------------------------

1) `POST /uploads/complete` handler
- validate `job_id` and `file_key`
- create `Document` row with `r2_key = file_key`
- compute checksum optionally
- determine splitting strategy (if pdf -> number of pages)
- create `Task` rows per page or per-file
- enqueue each task to queue: `queue.enqueue("process_task", task_id=task.id)`

2) Worker `process_task(task_id)`
- load Task and Document
- idempotency: if `ParseResult` exists for `task_id` -> return
- download source (R2) to temp
- call OCR client (with timeout, retry wrapper)
- on success -> upload parsed JSON to R2 `results/{job_id}/...` and write `ParseResult` row, mark Task completed
- on failure -> increment attempts, if attempts < max => re-enqueue with backoff, else mark Task.failed and write last_error

Client-side pseudocode (JS)
---------------------------
- Upload (presigned):
  1) POST `/uploads/presign` -> get `upload_url` + `job_id`.
  2) PUT `upload_url` file (fetch, axios, etc.)
  3) POST `/uploads/complete` { job_id, file_key }
  4) Poll: GET `/jobs/{job_id}` until `status=completed|failed`.

Examples (curl)
---------------

Presign:

```
curl -X POST "https://api.example.com/uploads/presign" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"filename":"doc.pdf","content_type":"application/pdf"}'
```

PUT to R2 (presigned URL)

```
curl -X PUT "https://r2-presigned-url" -H "Content-Type: application/pdf" --upload-file doc.pdf
```

Complete:

```
curl -X POST "https://api.example.com/uploads/complete" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"job_id":"...","file_key":"originals/.../doc.pdf"}'
```

Poll:

```
curl -X GET "https://api.example.com/jobs/{job_id}" -H "Authorization: Bearer $TOKEN"
```

Testing & validation
--------------------
- Unit tests:
  - validate upload request validation, DB creation.
  - worker idempotency and retry logic (mock OCR client).
- Integration tests (fast):
  - use in-memory queue or test Redis; send a small PDF, ensure tasks are created, workers process, final job completed.
- E2E test:
  - run with a small OCR test provider or a mocked HTTP server to emulate OCR API responses including 429 and 5xx to validate backoff.
- CI guard:
  - avoid calling real OCR provider in CI; mock external HTTP calls.

Quality gates (quick triage)
---------------------------
- Build: N/A (docs). Server code should run in local dev.
- Lint/Typecheck: ensure code follows project linters & types.
- Tests: add unit and integration tests for upload/worker flow.

Operational notes & cost controls
-------------------------------
- Track per-job OCR API calls and cost; add throttling at queue or worker level.
- Provide rate-limiting by user to avoid abuse.
- For high-volume customers consider batching or a dedicated OCR plan with provider.

Implementation checklist (practical)
----------------------------------
- [ ] Implement `POST /uploads/presign` and presigned PUT flow.
- [ ] Implement `POST /uploads/complete` to create Document + Tasks.
- [ ] Implement queue + worker with rate-limited OCR client.
- [ ] Implement `GET /jobs/{job_id}`.
- [ ] Add idempotency via `client_upload_id` or checksum.
- [ ] Add monitoring metrics and DLQ.
- [ ] Add webhook option and signing.
- [ ] Add tests and docs (`docs/upload-and-parse-flow.md`).

Next steps
----------
- Implement the API endpoint stubs and a worker prototype in `backend/app/ocrs`.
- Add TypeScript/Python SDK snippets for upload + polling.
- Create tests that mock the OCR provider to validate retry/backoff and idempotency.

---

Document created on: 2026-04-08
