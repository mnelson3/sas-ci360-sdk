# Technical Requirements Document — sasci360solexecute

| | |
| --- | --- |
| Document | TRD-SOLEXECUTE-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-execute` (`sasci360solexecute`) |

## 1. Functional requirements

| ID | Requirement | Method |
| --- | --- | --- |
| SOLEXECUTE-FR-1 | Execute a campaign; get execution status; cancel a running execution. | `execute_campaign`, `get_execution_status`, `cancel_execution` (+ `_async`) |
| SOLEXECUTE-FR-2 | Submit a batch job; get its status; cancel it; list batch jobs (with status filter). | `submit_batch_job`, `get_batch_job_status`, `cancel_batch_job`, `get_batch_jobs` (+ `_async`) |
| SOLEXECUTE-FR-3 | Schedule a job; list scheduled jobs (active-only filter); update/delete a schedule. | `schedule_job`, `get_scheduled_jobs`, `update_schedule`, `delete_schedule` (+ `_async`) |
| SOLEXECUTE-FR-4 | Get execution metrics (filterable by date range and campaign). | `get_execution_metrics` (+ `_async`) |

`api_base` default: `/marketingExecution`.

## 2. Non-functional requirements

Inherits SOLEXECUTE-NFR-1 through SOLEXECUTE-NFR-8 from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package as of 2026-09-20:

| ID | Status |
| --- | --- |
| SOLEXECUTE-NFR-4 (Testability, correct boundary) | **Fixed**: same `urljoin` api_base-dropping defect as `sol-data`, `sol-workflow`, and `sol-identity`. Fixed to plain string formatting. |
| Coverage | 66% → 100% on `base.py` (52 tests). |
| Config validation | `batch_size <= 0` raises `CI360ExecuteValidationError` — unique to this package among the `sol-*` clients (others validate different domain-specific bounds, e.g. `max_concurrent_workflows` in `sol-workflow`). |

## 3. Data requirements

`CI360ExecuteConfig`: the standard fields (see parent TRD.md §5) plus `batch_size` (default 1000), `max_concurrent_jobs` (default 10), `job_timeout` (default 3600).

## 4. Technology stack

Same as the parent repository.

## 5. Dependency policy

Same SOLEXECUTE-NFR-8 pattern as every `sol-*` package.

## 6. Testing strategy

`tests/test_base.py` — 52 tests, 100% line coverage. The 2-line `except ImportError: Encryption = None` fallback is marked `# pragma: no cover` (added 2026-09-20, matching `sol-data`'s existing convention) since it can't be exercised while `api-core` is actually installed.

`tests/test_live_tenant.py` — calls `get_batch_jobs`/`get_scheduled_jobs` and `validate_connection()` against a real tenant. See [sas-ci360-sdk/UAT.md](../../../UAT.md).

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
