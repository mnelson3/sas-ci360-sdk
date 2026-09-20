# Technical Requirements Document — sasci360solplanning

| | |
| --- | --- |
| Document | TRD-SOLPLANNING-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-planning` (`sasci360solplanning`) |

## 1. Functional requirements

| ID | Requirement | Method |
| --- | --- | --- |
| SOLPLANNING-FR-1 | List/get/create/update/delete campaigns (with filters on list). | `get_campaigns`, `get_campaign`, `create_campaign`, `update_campaign`, `delete_campaign` (+ `_async`) |
| SOLPLANNING-FR-2 | List/get/create/update/delete audiences (with filters on list); estimate an audience's size from criteria without creating it. | `get_audiences`, `get_audience`, `create_audience`, `update_audience`, `delete_audience`, `estimate_audience_size` (+ `_async`) |
| SOLPLANNING-FR-3 | Get campaign analytics. | `get_campaign_analytics` (+ `_async`) |
| SOLPLANNING-FR-4 | Trigger campaign optimization. | `optimize_campaign` (+ `_async`) |
| SOLPLANNING-FR-5 | List campaign templates (with filters); create a campaign from a template. | `get_campaign_templates`, `create_campaign_from_template` (+ `_async`) |

`api_base` default: `/marketingPlanning`.

## 2. Non-functional requirements

Inherits SOLPLANNING-NFR-1 through SOLPLANNING-NFR-8 from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package:

| ID | Status |
| --- | --- |
| SOLPLANNING-NFR-1 (Auth correctness) | **Real bug found and fixed during the monorepo migration** (commit `22b9a82`, before this session's testing pass): this package (and `sol-workflow`) generated JWTs with the wrong payload shape and an unencoded signing key. Fixed by delegating to `api-core`'s canonical `Encryption` class. |
| SOLPLANNING-NFR-4 (Testability, correct boundary) | **Real bug found and fixed during the monorepo migration** (commit `4105e81`, before this session's testing pass): `_make_request_async` used `urljoin(host + api_base, endpoint)`, dropping `/marketingPlanning` from every real request. Fixed to plain string formatting — the same defect and fix later found to be systemic across `sol-data`, `sol-execute`, `sol-workflow`, and `sol-identity` when 2026-09-20's testing pass checked whether it had spread. This package's fix, and its regression test, are the pattern that fix was modeled on. |
| Coverage | 65% as of 2026-09-20 (unchanged this pass — the mocking-boundary work done for the other 5 `sol-*` packages that session wasn't repeated here since the two defects above were already found, fixed, and regression-tested independently before this repository was consolidated). Closing the remaining gap the same way is a candidate for a future pass. |

## 3. Data requirements

`CI360PlanningConfig`: the standard fields (see parent TRD.md §5).

## 4. Technology stack

Same as the parent repository.

## 5. Dependency policy

Same SOLPLANNING-NFR-8 pattern as every `sol-*` package.

## 6. Testing strategy

`tests/test_base.py` includes a dedicated URL-construction regression test (`test_make_request_async_includes_api_base_in_url`) that mocks one level deeper than the rest of the file — at `session.request` directly — specifically because that's what caught the SOLPLANNING-NFR-4 bug above; every other test in the file mocks `_make_request_async` itself, which is appropriate for testing the higher-level methods but wouldn't have caught that defect.

`tests/test_live_tenant.py` — calls `get_campaigns`/`get_audiences` and `validate_connection()` against a real tenant. See [sas-ci360-sdk/UAT.md](../../../UAT.md).

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
