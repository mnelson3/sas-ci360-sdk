# Technical Requirements Document — sas-ci360-sdk

| | |
| --- | --- |
| Document | TRD-CI360SDK-1.0 |
| Owner | Nelson Grey LLC |
| Scope | Layers 1–2: `api-core` and the 7 domain-client packages |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20), scoped to this repository |

## 1. Overview & traceability

| BRD | TRD | Relationship |
| --- | --- | --- |
| BR-1 | FR-1, NFR-1 | Auth must work from UI-obtainable values only → static-JWT flow with no extra setup. |
| BR-2 | FR-2…FR-8 | Independent installability → each API category is its own package with its own minimal dependency set. |
| BR-3 | NFR-2 | No embedded credentials → security requirement, testable by grep, verified 2026-09-20. |
| BR-5 | NFR-7 | One implementation per API → this repository holds exactly one canonical package per category. |

## 2. Functional requirements

| ID | Requirement | Package |
| --- | --- | --- |
| FR-1 | Generate a static JWT from a tenant ID and client secret (base64-encoded key, HS256, `{"clientID": tenant_id}` payload) and attach it as a Bearer token to every outbound request. | `api-core::Encryption` |
| FR-2 | Authenticated CRUD against the Marketing Data API: tables, customer jobs, event jobs, export request jobs, identity records, import request jobs, file transfer location. | `sol-data` |
| FR-3 | Download Discover data-mart extracts (Detail, DBT Report, Snapshot/Identity) from the Marketing Gateway's discover service. | `marketing-gateway` |
| FR-4 | Trigger and query marketing execution tasks, batch jobs, scheduled jobs, execution metrics. | `sol-execute` |
| FR-5 | Read and drive CI360 Workflow processes, triggers, and templates. | `sol-workflow` |
| FR-6 | Manage Plan API objects (campaigns, audiences, analytics). | `sol-planning` |
| FR-7 | Manage digital assets, content delivery, and content templates via the Digital Assets API. | `sol-content-delivery` |
| FR-8 | Provision and query users, groups, and service-provider config via SCIM. | `sol-identity` |
| FR-9 | Persist every API response payload to a JSON report file, namespaced by folder and timestamp. | `api-core::Reporter` |
| FR-10 | Run scheduled, unattended jobs on a configurable interval. | `api-core::Scheduler` |

## 3. Non-functional requirements

| ID | Category | Requirement | Status as of 2026-09-20 |
| --- | --- | --- | --- |
| NFR-1 | Reliability | Every outbound HTTP call retries transient failures (429, 500, 502, 503, 504) with backoff before surfacing an error to the caller. | Verified: identical `Retry`+`HTTPAdapter` config present in all 7 packages. |
| NFR-2 | Security | Secrets are supplied only via environment variables or a gitignored config file; none appear in source, tests, or fixtures. | Verified: audited, clean. |
| NFR-3 | Observability | Every module logs errors with context. | Verified per-package. |
| NFR-4 | Testability | The HTTP layer must be mockable at the `requests` boundary so unit tests never require network access, **and** that mocking must happen at the actual `session.get`/`session.request` call, not at a higher-level method like `_make_request_async` that hides the logic underneath it. | Verified: all 7 packages now have direct tests at the `session` boundary (see DDD.md §Testing design) — this was a real gap until 2026-09-20; see the urljoin finding below. |
| NFR-5 | Compatibility | Python 3.8–3.11 supported and covered in CI. | Verified in CI matrices. |
| NFR-6 | Configurability | Safe fallback defaults when no config file is present; fails fast with a named error if `host`/`secret_key`/`tenant_id` is missing. | Verified per-package config-validation tests. |
| NFR-7 | Maintainability | Exactly one supported implementation per API category in this repository. | Verified — see DDD.md §Consolidation. |
| NFR-8 | Packaging hygiene | A dependency is declared only if the package's own code imports it; a package's `setup.cfg install_requires` and `requirements.txt` must not drift from each other. | **Real violations found and fixed 2026-09-20**: `api-core`/`marketing-gateway` had a malformed `[install_requires]` section (silently ignored by setuptools — zero deps installed by a bare `pip install`); `sol-content-delivery` was missing `sasci360apicore` and `requests-toolbelt` entirely; `sol-workflow` was missing `api-core`'s transitive deps. All fixed. |

## 4. Integration requirements

- **Access Point**: every client is constructed from a host (e.g. `extapigwservice-<env>.ci360.sas.com`), tenant ID, and client secret obtained from a CI360 Access Point.
- **Base path convention**: `https://{host}/{api_base}{endpoint}`, where `api_base` is fixed per client (e.g. `/marketingData`, `/marketingExecution`, `/scim`).
- **Token lifetime**: the static JWT does not expire and is regenerated per client instantiation, not cached to disk.
- **Rate limits**: not documented by SAS as fixed numbers; clients treat 429 as retryable rather than assume a specific quota.

## 5. Data requirements

Every domain-client config carries: `algorithm` (default `HS256`), `encoding` (default `utf-8`), `api_base`, `host`, `secret_key`, `tenant_id`, `timeout` (default 30s), `max_retries` (default 3), `retry_backoff` (default 0.5). `host`/`secret_key`/`tenant_id` are the only required fields; validation fails fast with a named error if any is missing.

## 6. Technology stack

| Layer | Technology |
| --- | --- |
| Runtime | Python 3.8–3.11, setuptools packaging, src-layout, per-package `pyproject.toml` |
| HTTP | `requests` + `urllib3`, a `requests.Session` with an `HTTPAdapter`-mounted `Retry` policy |
| Auth | `PyJWT`, HS256 signing over a base64-encoded secret |
| Data | `pandas` (tabular handling for Discover/data-mart output) |
| Test | `pytest` + `pytest-cov`, `unittest.mock` for HTTP, env-var-gated live-tenant tests |
| CI | GitHub Actions — flake8, mypy, pytest matrix across supported Python versions |

## 7. Environments

Three logical modes — `development`, `test`, `production` — each with independent host/secret/tenant values, selected at construction time via the config object. There is no environment-name kwarg on the base classes in this repository (that pattern lives in `sas-ci360-solutions`'s `Standard` config class instead).

## 8. Dependency policy

A dependency is added only when a specific, named import requires it, and reviewed for maintenance status before being pinned. `sas-dlpy` and `SAS-kernel` were found in earlier generations' `requirements.txt` files without being imported anywhere — removed. See NFR-8 above for the setup.cfg/requirements.txt drift bugs found and fixed on 2026-09-20.

## 9. Testing strategy

- **Unit tier** (must not require network): mock `requests.Session` **at the session-call boundary**, not at `_make_request_async`. Assert on request construction (headers, URL, payload) and response handling. All 7 packages are at 100% line coverage on `base.py` as of 2026-09-20.
- **Integration / UAT tier** (requires a real tenant): gated behind `CI360_HOST`/`CI360_SECRET_KEY`/`CI360_TENANT_ID`, skipped (not failed) when unset, never run in the default CI job. See [`UAT.md`](../UAT.md).
- **Private-dependency isolation**: `sol-identity`'s tests stub the private `sasci360apicore` dependency via `sys.modules` injection rather than requiring it installed — the pattern other packages' tests reuse for pywin32 (in `sas-ci360-solutions`) and cloud SDKs (in `sas-ci360-plan-connector`).

### The mocking-boundary lesson (2026-09-20)

Every test suite in this repository originally mocked `_make_request_async` itself for call-level tests, which is correct for testing *those* methods but left the connection-validation and URL-construction logic underneath completely unexercised. Writing tests one level deeper — at `session.get`/`session.request` — surfaced a real, previously undetected bug present in 5 of the 6 `sol-*` packages: `urljoin(host + api_base, endpoint)` silently drops `api_base` whenever `host` has no trailing slash (RFC 3986 relative-reference resolution treats a no-trailing-slash base as a document to replace, not a directory to extend). Every real request these five clients ever made against a live tenant was hitting the wrong URL. Fixed with plain string formatting instead of `urljoin`. NFR-4 above now states the boundary requirement explicitly so this doesn't recur.

## 10. CI/CD requirements

Every package runs the same four gates on push/PR to `main`, `staging`, `develop`: flake8 (hard errors E9/F63/F7/F82 always block), mypy, pytest with coverage, and a from-clean-environment dependency install. Internal (non-PyPI) dependencies install via a pinned VCS reference to this public repository.
