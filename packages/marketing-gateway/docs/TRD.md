# Technical Requirements Document — sasci360apimarketinggateway

| | |
| --- | --- |
| Document | TRD-MARKETINGGATEWAY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/marketing-gateway` (`sasci360apimarketinggateway`) |

## 1. Functional requirements

| ID | Requirement | Class / method |
| --- | --- | --- |
| MARKETINGGATEWAY-FR-1 | Get the API's top-level resource links. | `root.Root.get_root()` |
| MARKETINGGATEWAY-FR-2 | Download Discover base/detail/identity/reprocessed data-mart tables, with delta and time-range filtering via kwargs. | `data_download.DataDownload.get_base_tables()`, `.get_detail_tables()`, `.get_identity_tables()`, `.get_reprocessed_tables()` |
| MARKETINGGATEWAY-FR-3 | Inject a single external event or a bulk batch of events. | `events.Events.create_external_event(payload)`, `.create_bulk_events(payload)` |
| MARKETINGGATEWAY-FR-4 | Get the diagnostics, direct, general, and optimize agent configurations. | `agents.Agents.get_diagnostics_agent()`, `.get_direct_agent()`, `.get_general_agent()`, `.get_optimize_agent()` |
| MARKETINGGATEWAY-FR-5 | Get gateway configuration. | `configuration.Configuration.get_configuration()` |

Each class constructs independently from `(algorithm, api, encoding, host, secret_key, tenant_id)` — there's no single `MarketingGatewayBase` all five share; each is its own `Base` subclass. `api` is typically `/marketingGateway` but is passed explicitly rather than defaulted, since this generation predates the `api_base`-as-config-field convention.

## 2. Non-functional requirements

Inherits MARKETINGGATEWAY-NFR-1 through MARKETINGGATEWAY-NFR-8 from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package as of 2026-09-20:

| ID | Status |
| --- | --- |
| MARKETINGGATEWAY-NFR-8 (Packaging hygiene) | **Real bug found and fixed**: same malformed `[install_requires]` section as `api-core` (silently ignored by setuptools — a bare `pip install` installed zero dependencies). Fixed, and the stale 2022-era version pins updated to match `requirements.txt`. |
| MARKETINGGATEWAY-NFR-4 (Testability) | This package's tests mock `requests.get`/`requests.post` directly (predates the `Session`-object pattern the `sol-*` packages use) — a different but equally valid mocking boundary, since it's still below this package's own request-construction logic, not above it. |

## 3. Data requirements

No `Config` dataclass — each class's `__init__` takes `algorithm`, `api`, `encoding`, `host`, `secret_key`, `tenant_id` directly as constructor arguments.

## 4. Technology stack

Same as `api-core` — `requests`, `PyJWT`, `pandas`, `saspy`, `schedule`, `DateTime`, `urllib3`, plus `sasci360apicore` itself as a direct dependency (this package delegates auth entirely to `api-core`'s `connection`/`encryption` modules rather than reimplementing them).

## 5. Dependency policy

See MARKETINGGATEWAY-NFR-8 above.

## 6. Testing strategy

`tests/Test*.py` (one per module: `TestRoot.py`, `TestAgents.py`, `TestConfiguration.py`, `TestDataDownload.py`, `TestEvents.py`) — `unittest.TestCase`-style, patching `requests.get`/`requests.post` directly.

`tests/TestLiveTenant.py` — calls `Root.get_root()` against a real tenant, `unittest.skipUnless`-gated on `CI360_HOST`/`CI360_SECRET_KEY`/`CI360_TENANT_ID`. Added 2026-09-20. See [sas-ci360-sdk/UAT.md](../../../UAT.md). Note this package's `host` is a bare hostname, not a full URL — see DDD.md.

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
