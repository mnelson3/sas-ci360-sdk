# Detailed Design Document — sasci360solidentity

| | |
| --- | --- |
| Document | DDD-SOLIDENTITY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-identity` (`sasci360solidentity`) |

## Architecture

Standard Layer-2 domain-client pattern — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md). `CI360IdentityBase` subclasses `sasci360apicore.rest_client.RestClientBase` (added 2026-09-21), which owns `__init__`, config validation, session creation, JWT generation, `get_auth_headers`, `validate_connection(_async)`, and `_make_request(_async)` — this package now defines only its `Config` extras (`scim_version`), its own exception hierarchy (`CI360IdentityError`, `CI360IdentityAuthError`, `CI360IdentityConnectionError`, `CI360IdentityValidationError` — unchanged names, still raised via the shared code through 4 class attributes), and its SCIM domain methods. See `docs/DDD.md`'s "Extracting the shared REST client base" section for the full rationale and the six packages' migration history.

## Two SCIM-specific overrides

This package overrides two of `RestClientBase`'s extension points rather than taking the shared defaults, both because SCIM's shape genuinely differs from the other `sol-*` APIs':

```python
def get_auth_headers(self) -> Dict[str, str]:
    # SCIM wants application/scim+json and a SCIM-Version header,
    # not the shared class's application/json default
    ...

def _health_check_url(self) -> str:
    # SCIM has no bare /health endpoint; ServiceProviderConfig is
    # its well-known, unauthenticated-shape discovery endpoint,
    # under the SCIM service root - not the host root the shared
    # default's plain urljoin(host, "/health") hits
    return f"{self._base_url.rstrip('/')}/ServiceProviderConfig"
```

Before the shared base existed, this package also had its own `_base_url` property (`host + api_base`, without an `rstrip` before concatenating). Moving that into `RestClientBase` (rstripping host first, matching what the other 5 packages already did inline) incidentally fixed a latent double-slash edge case here, only reachable if a caller configured `host` with a trailing slash — no test exercised it either way.

## The api_base URL bug — historical

Before the shared base existed, this package had the `urljoin`/`api_base`-dropping defect (see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction) in two independent call sites, since `_make_request_async` and the SCIM health check each built their own URL. Both are long since fixed, and are now one shared, tested implementation (`_make_request_async`) plus one override (`_health_check_url`) rather than two places a similar bug could recur independently.

## Testing design

`tests/test_base.py` used to open with a `sys.modules` stub faking `sasci360apicore`/`sasci360apicore.encryption`, because the old `_generate_token()` imported `Encryption` lazily and this package's `requirements-dev.txt` deliberately didn't install the real `sasci360apicore` (see `sol-content-delivery`'s DDD for the module-level-import-guard variant other packages used instead, and `sas-ci360-solutions`'/`sas-ci360-plan-connector`'s docs for where the same general stubbing technique was reused for pywin32 and cloud SDKs). That stub is removed: `CI360IdentityBase` now subclasses `RestClientBase` directly, so `sasci360apicore` must be a real, importable package for this package's own classes to be defined at all, not just mockable away at call time. `requirements-dev.txt` now installs the real `sasci360apicore` (and its own transitive deps — `sasci360apicore`'s `__init__.py` eagerly imports every one of its submodules, so even needing only `rest_client` pulls in the full set). Test patches for `requests.Session`/`Encryption`/`asyncio.run` now target `sasci360apicore.rest_client`, since that's where the shared code that uses them actually lives; patches on `CI360IdentityBase._make_request_async`/`validate_connection(_async)` were untouched, since those resolve correctly via inheritance regardless of which class defines the method.

## CI/CD pipeline

Same as every package in this repository.
