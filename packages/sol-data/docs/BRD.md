# Business Requirements Document — sasci360soldata

| | |
| --- | --- |
| Document | BRD-SOLDATA-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-data` (`sasci360soldata`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`sol-data` is the canonical client for CI360's Marketing Data API — customer records, segments, bulk import/export, table and import-request-job management, and file-transfer-location signed uploads. It's the client `sas-ci360-solutions`' identity-bridge orchestration is built on.

## 2. Business context

Marketing Data is the API surface an implementer touches for anything involving customer records or bulk data movement — it's the highest-traffic API category in this toolkit's own reference orchestration (identity-bridge). It supersedes `sas-ci360-api-marketing-data` (archived), the earlier generation covering the same API without mockable tests or typed exceptions.

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| BG-1 | Cover the customer, segment, import/export, schema, import-request-job, file-transfer, and table operations an implementer needs for a real identity-bridge or bulk-data integration. | API surface parity with what `sas-ci360-solutions` actually calls |
| BG-2 | Every operation verifiable without a live tenant. | 100% line coverage on `base.py` (achieved 2026-09-20) |
| BG-3 | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT tests present (achieved 2026-09-20) |

## 4. Stakeholders

- **`sas-ci360-solutions`** — the primary real-world consumer; its identity-bridge cycle calls `get_import_request_jobs`, `create_import_request_job`, `create_file_transfer_location`, and `upload_to_signed_url` directly.
- **Implementation engineer** doing bulk customer/segment data work independent of the identity-bridge use case.

## 5. Scope

### In scope
Customer CRUD, segment CRUD, bulk import/export, data validation, schema get/update, import-request-job listing/creation/retrieval, file-transfer-location signed-URL creation and upload, table listing/CRUD.

### Out of scope
Anything outside the Marketing Data API — see the parent repo's [BRD.md](../../../docs/BRD.md) §5 for the full family scope.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| BR-1 | `upload_to_signed_url` must upload directly to the signed URL `create_file_transfer_location` returns, without CI360 auth headers (the signed URL is itself pre-authenticated). | P1 |
| BR-2 | Every request must land under `/marketingData`, not just at `host`'s root. | P1 (real bug found and fixed, see TRD.md) |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

Assumes the caller already has a signed URL from `create_file_transfer_location()` before calling `upload_to_signed_url()` — this package doesn't manage that lifecycle for you.

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
