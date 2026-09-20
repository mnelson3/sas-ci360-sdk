# Technical Requirements Document — sasci360soldata

| | |
| --- | --- |
| Document | TRD-SOLDATA-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-data` (`sasci360soldata`) |

## 1. Functional requirements

| ID | Requirement | Method |
| --- | --- | --- |
| `SOLDATA-FR-1` | List/get/create/update/delete customers. | `get_customers`, `get_customer`, `create_customer`, `update_customer`, `delete_customer` (+ `_async`) |
| `SOLDATA-FR-2` | List/get/create/update/delete segments. | `get_segments`, `get_segment`, `create_segment`, `update_segment`, `delete_segment` (+ `_async`) |
| `SOLDATA-FR-3` | Bulk import/export/validate data. | `import_data`, `export_data`, `validate_data` (+ `_async`) |
| `SOLDATA-FR-4` | Get/update a data schema. | `get_schema`, `update_schema` (+ `_async`) |
| `SOLDATA-FR-5` | List/create/get import request jobs. | `get_import_request_jobs`, `create_import_request_job`, `get_import_request_job` (+ `_async`) |
| `SOLDATA-FR-6` | Create a signed upload URL and upload a local file to it directly (bypassing this client's normal auth headers, since the signed URL is itself pre-authenticated). | `create_file_transfer_location`, `upload_to_signed_url` (+ `_async`) |
| `SOLDATA-FR-7` | List/get/create/update/delete tables. | `get_tables`, `get_table`, `create_table`, `update_table`, `delete_table` (+ `_async`) |

`api_base` default: `/marketingData`.

## 2. Non-functional requirements

Inherits `SOLDATA-NFR-1` through `SOLDATA-NFR-8` from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package as of 2026-09-20:

| ID | Status |
| --- | --- |
| `SOLDATA-NFR-4` (Testability, correct boundary) | **Fixed**: `_make_request_async` used `urljoin(host + api_base, endpoint)`, which silently dropped `api_base` — every real request was hitting `https://{host}/{endpoint}` instead of `https://{host}/marketingData/{endpoint}`. Fixed to plain string formatting. Found by testing at the `session.request` boundary instead of mocking `_make_request_async` itself. |
| Coverage | 66% → 100% on `base.py` (90 tests). |

## 3. Data requirements

`CI360DataConfig`: `algorithm` (default `HS256`), `api_base` (default `/marketingData`), `encoding`, `host`, `secret_key`, `tenant_id`, `timeout` (30s), `max_retries` (3), `retry_backoff` (0.5), `enable_compression` (`True`).

## 4. Technology stack

Same as the parent repository — `requests`, `urllib3`, `PyJWT`, `pandas`, `saspy`, `schedule`, `DateTime`. Full list in `requirements.txt`.

## 5. Dependency policy

`requirements.txt` re-declares `api-core`'s own dependencies (`pandas`, `saspy`, `schedule`, `DateTime`) redundantly — see [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md) `SOLDATA-NFR-8` for why.

## 6. Testing strategy

`tests/test_base.py` — 90 tests, 100% line coverage on `base.py`, including real (non-tautological) `validate_connection_async` tests, the full `_make_request_async` status-code-to-exception mapping (401/5xx/other 4xx/network error/reconnect-on-disconnected), both `_generate_token` failure modes, real context-manager success/failure paths, and every sync wrapper and filter-merge branch.

`tests/test_live_tenant.py` — UAT tier, calls `get_tables`/`get_customers` and `validate_connection()` against a real tenant, gated behind `CI360_HOST`/`CI360_SECRET_KEY`/`CI360_TENANT_ID`. See [sas-ci360-sdk/UAT.md](../../../UAT.md).

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
