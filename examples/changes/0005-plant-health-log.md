# Change 0005 - Plant Health Log

## Summary
Add a health log feature allowing users to record timestamped observations about their plants - a health score, free-text notes, and an optional photo. Logs are returned as a paginated list per plant.

## Motivation
Users need to track plant progress over time to correlate care actions with health outcomes. This is the third most-requested feature on the feedback board (47 upvotes). Without it, users have no way to know whether their current care routine is working.

## Scope
- **Components affected**: API (new endpoints), database (new table), storage (photo uploads)
- **Files likely touched**:
  - `app/models/plant_log.py` (new model)
  - `app/routes/plant_logs.py` (new router)
  - `app/main.py` (register router)
  - `app/storage.py` (photo upload helper)
  - `alembic/versions/XXXX_add_plant_logs.py` (migration)
- **Backwards compatibility**: Existing plant endpoints are unchanged. New endpoints added under `/plants/{id}/logs`.

## Proposed Approach
1. Create a `plant_logs` table: `id`, `plant_id`, `user_id`, `logged_at`, `health_score` (1-5 integer), `notes` (text, nullable), `photo_url` (nullable).
2. Add four endpoints:
   - `POST /plants/{id}/logs` - create a log entry (with optional photo upload)
   - `GET /plants/{id}/logs` - list logs for a plant, paginated (20 per page), newest first
   - `GET /plants/{id}/logs/{log_id}` - get a single log entry
   - `DELETE /plants/{id}/logs/{log_id}` - delete a log entry and its photo (if any)
3. Photo uploads: accept JPEG/PNG up to 5 MB; validate MIME type server-side (not just extension); store in S3-compatible storage; return a pre-signed URL with a 1-hour TTL.
4. All endpoints enforce plant ownership via the existing `require_plant_owner` dependency.

## Why This Approach
Storing logs as a child table of plants is the simplest model that supports the required queries. Photo storage in S3 keeps the database row small and allows CDN delivery. Pre-signed URLs avoid exposing bucket credentials to clients while limiting photo accessibility to a reasonable window.

An alternative was to store photos as base64 in the database - rejected because it inflates row size, complicates backups, and prevents CDN caching.

## Security Impact
- **Risks reduced**: A01 (Broken Access Control) - plant ownership is checked on every operation; A04 (Insecure Design) - photo uploads validated for MIME type and size server-side.
- **New risks introduced**: Enumerable plant IDs could allow cross-user data discovery. Mitigated by returning 404 (not 403) for plants the requesting user does not own, preventing confirmation of existence.
- **OWASP mapping**: A01-Broken Access Control, A04-Insecure Design, A05-Security Misconfiguration (pre-signed URL TTL).
- **Controls implemented**: #4 (server-side input validation), #33 (object-level authorisation on every endpoint).

## Performance & Reliability Impact
- **Latency / resource considerations**: Photo uploads are synchronous in v1; large files (up to 5 MB) will add latency on the create endpoint. Acceptable for now - async upload can be added if p95 latency exceeds 2 s.
- **Failure modes**: If the S3 upload fails after the database row is created, the log entry will have a null `photo_url`. A cleanup job can be added later; for v1 this is acceptable data state.

## Acceptance Criteria

| ID | Criterion (Given / When / Then) | Test ID |
|----|--------------------------------|---------|
| AC-01 | Given an authenticated user who owns plant `p1`, when `POST /plants/p1/logs` with `health_score=4` and `notes="Looking good"`, then the response is `201 Created` with a body containing the new log's `id` and `logged_at`. | T-005-01 |
| AC-02 | Given plant `p1` with three existing logs, when `GET /plants/p1/logs`, then the response is `200 OK` with logs ordered newest-first and a `total` count in the response envelope. | T-005-02 |
| AC-03 | Given an authenticated user who owns plant `p1`, when `POST /plants/p1/logs` includes a JPEG attachment of 6 MB, then the response is `422 Unprocessable Entity` with `"photo exceeds 5 MB limit"` in the error detail. | T-005-03 |
| AC-04 | Given plant `p1` owned by user A, when user B (authenticated, different account) calls `GET /plants/p1/logs`, then the response is `404 Not Found` (not `403`). | T-005-04 |
| AC-05 | Given a log with a photo, when `DELETE /plants/p1/logs/{log_id}`, then the response is `204 No Content` and the photo object is removed from storage within 5 seconds. | T-005-05 |
| AC-06 | Given a JPEG file whose extension has been renamed to `.png`, when uploaded as a photo, then the server rejects it with `422` citing invalid MIME type. | T-005-06 |

## Effort

- **Estimated hours**: 6
- **Actual hours**: 5.5

## Testing
- **Unit tests**: Model validation (health_score bounds 1-5, notes max length), photo MIME type detection, ownership dependency logic.
- **Integration tests**: Full CRUD flow for logs; pagination (boundary: exactly 20 items); photo upload and deletion; cross-user access attempt (AC-04).
- **Negative / abuse cases**: Upload a file with a spoofed MIME type (AC-06); delete a log that belongs to a different user; request a log with a non-existent plant ID; upload a zero-byte file.

## Operational Notes
- **Config knobs / flags**: `BLOOM_STORAGE_BUCKET` (S3 bucket name), `BLOOM_PHOTO_URL_TTL_SECONDS` (pre-signed URL TTL, default `3600`).
- **Metrics / logs added**: Log storage upload latency at INFO level; log a WARNING if S3 upload fails but DB row was committed.
- **Alerts to consider**: Alert if photo storage error rate exceeds 1% over a 5-minute window - indicates a storage configuration problem, not user error.

## Rollback Plan
1. Deploy the previous API version (no changes to existing endpoints, so rollback is safe).
2. Run the Alembic downgrade: `alembic downgrade -1` - this drops the `plant_logs` table and its data.
3. Remove the `BLOOM_STORAGE_BUCKET` env var to prevent orphaned upload attempts.

Expected side effects: Any plant logs created since deployment will be lost. Acceptable for v1 where data volume is low; communicate to any affected users.

## Approval
- **Status**: Implemented
- **Approved by**: Jordan (project owner)
- **Date**: 2025-04-08

---
*Template: `templates/documents/change-proposal.md`*
