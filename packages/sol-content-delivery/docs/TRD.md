# Technical Requirements Document — sasci360solcontentdelivery

| | |
| --- | --- |
| Document | TRD-SOLCONTENTDELIVERY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-content-delivery` (`sasci360solcontentdelivery`) |

## 1. Functional requirements

| ID | Requirement | Method |
| --- | --- | --- |
| `SOLCONTENTDELIVERY-FR-1` | List/get/upload/update/delete assets. | `get_assets`, `get_asset`, `upload_asset`, `update_asset`, `delete_asset` (+ `_async`) |
| `SOLCONTENTDELIVERY-FR-2` | Send content for delivery; get delivery status; list deliveries (status filter). | `deliver_content`, `get_delivery_status`, `get_deliveries` (+ `_async`) |
| `SOLCONTENTDELIVERY-FR-3` | List content templates (category filter); create content from a template. | `get_content_templates`, `create_content_from_template` (+ `_async`) |
| `SOLCONTENTDELIVERY-FR-4` | Get content analytics (filterable by asset and date range). | `get_content_analytics` (+ `_async`) |

`api_base` default: `/digital-assets`.

## 2. Non-functional requirements

Inherits `SOLCONTENTDELIVERY-NFR-1` through `SOLCONTENTDELIVERY-NFR-8` from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package as of 2026-09-20:

| ID | Status |
| --- | --- |
| `SOLCONTENTDELIVERY-NFR-4` (Testability, correct boundary) | **This package is where the urljoin defect was first found in 2026-09-20's testing pass**, in two mechanisms: `_make_request_async`'s relative-reference form, and `upload_asset_async`'s absolute-reference form (`urljoin(host + api_base, "/assets/upload")`). Both fixed with plain string formatting. |
| `SOLCONTENTDELIVERY-NFR-8` (Packaging hygiene) | **2 real bugs found and fixed**: `setup.cfg` was missing `sasci360apicore` from its own `install_requires` (only `requirements.txt` had it — a standalone `pip install` would fail the moment `_generate_token()` ran); `requests-toolbelt` (imported by `upload_asset_async`) was declared nowhere at all. Both added to `requirements.txt` and `setup.cfg`. |
| Coverage | 57% → 100% on `base.py` (52 tests) — the lowest starting point of any `sol-*` package. |

## 3. Data requirements

`CI360ContentDeliveryConfig`: the standard fields plus `enable_compression` (`True`), `max_file_size_mb` (default 100), `supported_formats` (default: jpg, jpeg, png, gif, pdf, html, txt, mp4, avi).

## 4. Technology stack

Same as the parent repository, plus `requests-toolbelt` (for `upload_asset_async`'s multipart encoding) — see `SOLCONTENTDELIVERY-NFR-8` above.

## 5. Dependency policy

See `SOLCONTENTDELIVERY-NFR-8` above — this package is the reference example in this repository for what happens when `setup.cfg` and `requirements.txt` drift from each other.

## 6. Testing strategy

`tests/test_base.py` — 52 tests, 100% line coverage, including config validation error branches, `get_auth_headers`, connection-validation success/failure/exception paths, the full `_make_request_async` status-code-to-exception mapping, every previously-untested sync wrapper, the 4 context-manager methods, and `upload_asset` (previously entirely untested — the method that turned up the missing `requests-toolbelt` dependency).

`tests/test_live_tenant.py` — calls `get_assets`/`get_content_templates` and `validate_connection()` against a real tenant. See [sas-ci360-sdk/UAT.md](../../../UAT.md).

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
