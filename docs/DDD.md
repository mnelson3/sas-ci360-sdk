# Detailed Design Document — sas-ci360-sdk

| | |
| --- | --- |
| Document | DDD-CI360SDK-1.0 |
| Owner | Nelson Grey LLC |
| Scope | Layers 1–2: `api-core` and the 7 domain-client packages |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20), scoped to this repository |

## Architecture overview

```
Layer 2 — Domain clients (one per CI360 REST API)
  sol-data · marketing-gateway · sol-execute · sol-workflow
  sol-planning · sol-content-delivery · sol-identity
        │
        ▼
Layer 1 — Core (api-core)
  Connection · Communication · Encryption · Reporter · Scheduler · Logger
        │
        ▼
  SAS CI360 REST APIs
```

`sas-ci360-solutions` (Layer 3, orchestration) and `sas-ci360-plan-connector` (Layer 4, connectors) build on top of the packages here, from their own repositories.

- **Layer 1 — Core**: authentication, HTTP transport with retry, email notification, JSON report persistence, scheduling primitives. No CI360-domain knowledge lives here.
- **Layer 2 — Domain clients**: one package per REST API category. Each owns its own config, endpoint paths, and typed exceptions; depends on Layer 1 only.

## Consolidation

Three generations of overlapping code previously existed as 17 separate repositories. This repository is the executed result of consolidating 8 of them — `api-core` plus the 6 `sol-*` clients plus `marketing-gateway` — into one, on 2026-09-20, with each package's full git history preserved via `git filter-repo`.

| Concern | Canonical (this repo) | Retired |
| --- | --- | --- |
| Domain API clients | `sol-*` | `api-*` equivalents, archived (`-archived` suffix, kept public) |
| Core primitives | `api-core` | Duplicated Connection/Security/Reporter logic inside `automation-engine` (archived) |

Rationale: `sol-*` is the only generation with mockable unit tests, typed exceptions, and safe config fallbacks. The migration itself surfaced a real authentication defect in `sol-workflow`/`sol-planning` — both were generating JWTs with the wrong payload shape and an unencoded signing key, which CI360 would have rejected despite both passing their own mocked unit tests — fixed by delegating to `api-core`'s canonical `Encryption` class, as every other client already did.

## Core library design

`api-core` exposes six independent primitives:

| Class | Responsibility | Key methods |
| --- | --- | --- |
| `Connection` | HTTP call with bounded retry | `connect(action, url, headers, data, params)` |
| `Encryption` | Static JWT generation | `generate_jwt(secret_key, tenant_id)` |
| `Communication` | Outbound email (SMTP) | `send_email(...)` |
| `Reporter` | Persist a response payload as JSON | `save(folder, name, data)` |
| `Scheduler` | Recurring job execution | `chain_run()` / `change_run()` |
| `Data` | File processing helpers (CSV delimiter conversion, SAS dataset creation) | `create_csv()`, `create_sas_dataset()`, `get_schema()` |

`Reporter.save()` and every log-file handler must create their target directory before writing to it — a fresh checkout has no pre-existing `data/`/`logs/` tree.

## Domain client pattern

Every `sol-*` client (and, with a different Layer-1 dependency shape, `marketing-gateway`) follows the same shape. Through 2026-09-20 each package's `base.py` defined this shape independently — ~300 near-identical lines per package, six times over. That's now factored into one shared base:

```python
# api-core: sasci360apicore/rest_client/__init__.py
@dataclass
class RestClientConfig:
    algorithm: str = "HS256"
    api_base: str = ""
    encoding: str = "utf-8"
    host: Optional[str] = None
    secret_key: Optional[str] = None
    tenant_id: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 0.5

class RestClientBase:
    _CONFIG_CLS = RestClientConfig
    _ERROR_CLS = RestClientError
    _AUTH_ERROR_CLS = RestClientAuthError
    _CONNECTION_ERROR_CLS = RestClientConnectionError
    _VALIDATION_ERROR_CLS = RestClientValidationError

    def __init__(self, config=None):
        self.config = config or self._CONFIG_CLS()
        self._validate_config()                 # fails fast: host/secret_key/tenant_id required,
                                                  # then calls the _validate_extra_config() hook
        self.session = self._create_session()    # requests.Session + Retry-mounted HTTPAdapter
        self.token = self._generate_token()      # via Encryption

    def get_auth_headers(self) -> dict: ...
    def _health_check_url(self) -> str: ...       # hook; default urljoin(host, "/health")
    async def validate_connection_async(self) -> bool: ...
    def validate_connection(self) -> bool: ...
    async def _make_request_async(self, method, endpoint, data=None, params=None): ...
    def _make_request(self, method, endpoint, data=None, params=None): ...

# each sol-* package: sasci360sol<domain>/base.py
@dataclass
class CI360<Domain>Config(RestClientConfig):
    api_base: str = "/marketing<Domain>"
    # ...this package's own extra fields only

class CI360<Domain>Error(Exception): pass
class CI360<Domain>AuthError(CI360<Domain>Error): pass
class CI360<Domain>ConnectionError(CI360<Domain>Error): pass
class CI360<Domain>ValidationError(CI360<Domain>Error): pass

class CI360<Domain>Base(RestClientBase):
    _CONFIG_CLS = CI360<Domain>Config
    _ERROR_CLS = CI360<Domain>Error
    _AUTH_ERROR_CLS = CI360<Domain>AuthError
    _CONNECTION_ERROR_CLS = CI360<Domain>ConnectionError
    _VALIDATION_ERROR_CLS = CI360<Domain>ValidationError
    # ...this package's own domain methods only (get_customers, execute_campaign, ...)
```

Both sync and async request paths are supported from the same base class; async wraps the sync session call in an executor rather than requiring a separate async HTTP client, keeping the dependency surface small.

Each package keeps its own exact exception classes (so `except CI360DataAuthError` still works exactly as before — nothing catches the generic `RestClientAuthError` unless it's genuinely that generic) and its own `Config` extras, but no longer duplicates connection setup, JWT generation, request dispatch, or error mapping. Two extension points, not pure duplication, is what the six packages actually needed: `_validate_extra_config()` (every package had its own extra check — `batch_size`, `max_campaigns_per_user`, `scim_version`, etc. — appended after the shared required-fields/algorithm validation) and `_health_check_url()` (`sol-identity`'s SCIM connection check hits `ServiceProviderConfig` under the API base, not a bare host-root `/health` like the other five).

### URL construction: a fixed defect in this shared pattern

`_make_request_async` originally built the request URL with `urljoin(host + api_base, endpoint)`, independently in each package. Under RFC 3986 relative-reference resolution, `urljoin` treats a base URL with no trailing slash as a document to be replaced, not a directory to extend — so this silently dropped `api_base` from every request whenever `host` had no trailing slash (the normal case). This was present in `sol-data`, `sol-execute`, `sol-workflow`, and `sol-identity` (twice — once in the main request path, once in its SCIM `ServiceProviderConfig` health check, via the absolute-path-reference variant of the same defect); `sol-planning` had already been fixed independently before this was found to be systemic. Every affected client's real API calls against a live tenant were hitting the wrong path until 2026-09-20.

**Fix**: build the URL with plain string formatting, never `urljoin`, for anything that needs `api_base` preserved:

```python
url = f"{host.rstrip('/')}{api_base}/{endpoint.lstrip('/')}"
```

`urljoin(host, "/health")` (an absolute-path reference, deliberately replacing the whole path to hit a host-root health endpoint) is the one legitimate use of `urljoin` in this codebase — don't generalize away from it, only from the api_base-preserving case above. As of the `RestClientBase` extraction later on 2026-09-20, both the correct URL-building logic and this `urljoin` caveat live in exactly one place, via a `_base_url` property (`host.rstrip('/') + api_base`) every domain method and the shared request/health-check machinery use — a defect shaped like this one can no longer recur independently per package the way it did here.

## Error handling

A typed exception hierarchy per domain: `CI360<Domain>Error` base, with `…AuthError`, `…ConnectionError`, `…ValidationError` subclasses, raised with a specific message at the point of failure. `_make_request_async` maps HTTP status codes to these: 401 → `AuthError`, ≥500 → `ConnectionError`, other 4xx → the base `Error`, network-level exceptions → `ConnectionError`.

**Anti-pattern retired**: legacy generations wrapped entire methods in `except (AttributeError, Exception):` and returned `None` on any failure, including programming errors. New code catches specific exceptions and lets unexpected ones propagate.

## Security design

- Every credential-shaped config field is read from an environment variable or a gitignored config file, with a committed `.example` template using placeholder values.
- Config classes provide safe, non-secret fallback defaults so a missing config file degrades to "clearly not configured," never a crash or a real-looking placeholder.
- No test fixture reuses a real tenant ID, secret, or client name.

## Testing design

Unit tests patch `requests.Session` (or the specific verb method) **at the point the client actually calls it** — `session.get`/`session.request` — not at a higher-level method like `_make_request_async`, which was the anti-pattern found and retired across this repository on 2026-09-20 (see TRD.md §9). Doing so at the correct boundary is what surfaced both the urljoin defect above and several missing-dependency bugs (TRD.md CI360SDK-NFR-8). Since the `RestClientBase` extraction, that patch target is `sasci360apicore.rest_client.requests.Session`/`.Encryption`/`.asyncio.run` for every `sol-*` package (the shared code is where these names are actually referenced now) — patches on a package's own `_make_request_async`/`validate_connection(_async)` are unaffected, since those resolve correctly via inheritance regardless of which class defines the method.

`sol-identity`'s tests used to stub `sasci360apicore`/`sasci360apicore.encryption` via `sys.modules` injection, so its tests never required the real internal package to be installed (its `_generate_token()` imported `Encryption` lazily, only at token-generation time). That stub is gone: `CI360IdentityBase` subclasses `RestClientBase` directly now, so `sasci360apicore` must be a real, importable package for the class to even be defined, not just mockable away at call time — the same is true, and always was, for the other five packages. `sol-identity`'s `requirements-dev.txt` installs the real `sasci360apicore` now (and its full transitive dependency set — `sasci360apicore`'s own `__init__.py` eagerly imports every one of its submodules, so importing any single one of them, `rest_client` included, pulls in all of it).

Live-tenant / UAT tests (`tests/test_live_tenant.py`) read credentials from environment variables with a `pytest.mark.skipif` that makes the whole file a no-op when unset — see [`UAT.md`](../UAT.md).

## CI/CD pipeline

```
checkout → setup-python (3.8-3.11 matrix) → pip install -r requirements.txt
  → flake8 (hard: E9,F63,F7,F82) → mypy (+ types-requests, pandas-stubs)
  → pytest --cov → codecov upload
```

Every step is reproducible from a clean environment with no assumption of an editable local install or a sibling repository on disk.

## Package template

```
packages/<domain>/
├── src/sasci360<domain>/
│   ├── __init__.py
│   └── base.py                  # Config dataclass + Base class
├── tests/
│   ├── test_base.py             # mocked unit tests, 100% coverage target
│   └── test_live_tenant.py      # env-var-gated UAT tests
├── pyproject.toml                # [tool.pytest.ini_options] pythonpath = ["src"]
├── requirements.txt              # only what base.py actually imports
├── setup.cfg                     # install_requires must match requirements.txt
├── README.md
├── docs/
│   ├── BRD.md
│   ├── TRD.md
│   └── DDD.md
└── LICENSE
```
