# Business Requirements Document — sasci360solcontentdelivery

| | |
| --- | --- |
| Document | BRD-SOLCONTENTDELIVERY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-content-delivery` (`sasci360solcontentdelivery`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`sol-content-delivery` is the canonical client for CI360's Digital Assets API — asset management (including multipart file upload), content delivery, content templates, and content analytics.

## 2. Business context

Digital Assets is CI360's API for managing the images, documents, and other files campaigns reference, plus tracking their delivery and engagement. It supersedes `sas-ci360-api-digital-assets` (archived).

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| BG-1 | Cover asset CRUD (including file upload), content delivery, templates, and analytics. | API surface parity with CI360's Digital Assets API |
| BG-2 | Every operation verifiable without a live tenant. | 100% line coverage on `base.py` (achieved 2026-09-20) |
| BG-3 | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT tests present (achieved 2026-09-20) |
| BG-4 | `pip install` this package alone (without its sibling `requirements.txt`) must actually pull in everything it needs. | 0 NFR-8 violations (2 were found and fixed — see TRD.md) |

## 4. Stakeholders

- **Implementation engineer** uploading or managing digital assets, or tracking content delivery/analytics.

## 5. Scope

### In scope
Asset CRUD, including multipart file upload; content delivery send/status/listing; content template listing and content-from-template creation; content analytics.

### Out of scope
See the parent repo's [BRD.md](../../../docs/BRD.md) §5.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| BR-1 | Every request — including the multipart upload endpoint — must land under `/digital-assets`, not just at `host`'s root. | P1 (real bug found and fixed, see TRD.md) |
| BR-2 | This package's declared dependencies must actually cover everything its code imports (`sasci360apicore`, `requests-toolbelt`). | P1 (real bug found and fixed, see TRD.md) |
| BR-3 | `max_file_size_mb` config must be validated positive before use. | P2 |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

Assumes a `multipart/form-data` upload is an acceptable way to submit an asset file to CI360 — this is what `upload_asset` implements via `requests-toolbelt`'s `MultipartEncoder`.

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
