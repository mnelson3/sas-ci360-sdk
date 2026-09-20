# Technical Requirements Document — sasci360solidentity

| | |
| --- | --- |
| Document | TRD-SOLIDENTITY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-identity` (`sasci360solidentity`) |

## 1. Functional requirements

| ID | Requirement | Method |
| --- | --- | --- |
| FR-1 | List/get/create/update/PATCH/delete users. | `get_users`, `get_user`, `create_user`, `update_user`, `patch_user`, `delete_user` (+ `_async`) |
| FR-2 | List/get/create/update/delete groups. | `get_groups`, `get_group`, `create_group`, `update_group`, `delete_group` (+ `_async`) |
| FR-3 | Authenticate a user; validate/refresh a token. | `authenticate_user`, `validate_token`, `refresh_token` (+ `_async`) |
| FR-4 | Get the SCIM service-provider configuration. | `get_service_provider_config` (+ `_async`) |
| FR-5 | Perform a bulk SCIM operation. | `bulk_operation` (+ `_async`) |

`api_base` default: `/scim`.

## 2. Non-functional requirements

Inherits NFR-1 through NFR-8 from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package as of 2026-09-20:

| ID | Status |
| --- | --- |
| NFR-4 (Testability, correct boundary) | **Fixed, twice over** — the only package where the urljoin defect appeared in two places: `_make_request_async`'s main URL construction, and `validate_connection_async`'s SCIM `ServiceProviderConfig` health check (via the absolute-path-reference variant of the same defect — `urljoin` also replaces the whole path when its second argument is itself absolute). Both fixed with plain string formatting. |
| NFR-4 (Testability, no private dependency required) | This package's `requirements-dev.txt` deliberately excludes `sasci360apicore`/`saspy`/`pandas`/`schedule`/`DateTime` — unit tests mock the private encryption dependency via `sys.modules` injection instead of requiring it installed. This is the pattern this repository's other packages (`sol-content-delivery`'s tests, and `sas-ci360-solutions`'/`sas-ci360-plan-connector`'s test suites) later reused for their own uninstalled-dependency problems. |
| Coverage | 66% → 74% (urljoin regression tests) → 100% on `base.py` (61 tests). |

## 3. Data requirements

`CI360IdentityConfig`: the standard fields plus `scim_version` (default `2.0`, also accepts `1.1`).

## 4. Technology stack

Same as the parent repository, minus `saspy`/`pandas`/`schedule`/`DateTime` for unit testing (see NFR-4 above) — those remain real production dependencies via `requirements.txt`, just not needed to run this package's own tests.

## 5. Dependency policy

See NFR-4 above — this package's `requirements-dev.txt` is the reference example in this repository for testing without a private dependency installed.

## 6. Testing strategy

`tests/test_base.py` — 61 tests, 100% line coverage, including real (non-tautological) connection-validation tests, the full `_make_request_async` status-code-to-exception mapping, `_generate_token`'s failure-wrapping path, real async context-manager success/failure paths (previously only the sync ones were tested), and every previously-untested sync wrapper and filter-merge branch.

`tests/test_live_tenant.py` — calls `get_users`/`get_service_provider_config` and `validate_connection()` against a real tenant. See [sas-ci360-sdk/UAT.md](../../../UAT.md).

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
