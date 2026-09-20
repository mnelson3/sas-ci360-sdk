# Detailed Design Document — sasci360solidentity

| | |
| --- | --- |
| Document | DDD-SOLIDENTITY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-identity` (`sasci360solidentity`) |

## Architecture

Standard Layer-2 domain-client pattern — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md). Exception hierarchy: `CI360IdentityError`, `CI360IdentityAuthError`, `CI360IdentityConnectionError`, `CI360IdentityValidationError`. `_generate_token()` uses a lazy `from sasci360apicore.encryption import Encryption` import inside the method body (not the module-level try/except guard `sol-data`/`sol-execute`/`sol-workflow` use) — either failure mode is caught by the same broad `except Exception` and wrapped as `CI360IdentityAuthError`.

## `_base_url` property

Unlike the other `sol-*` packages, this one centralizes the host+api_base concatenation into one property, used by both `_make_request_async` and `validate_connection_async`:

```python
@property
def _base_url(self) -> str:
    assert self.config.host is not None
    return self.config.host + self.config.api_base
```

This is why the urljoin defect (below) had to be fixed in two call sites that both derive from this one property, rather than just one.

## The api_base URL bug — two mechanisms in one package

**Mechanism 1** (`_make_request_async`): `urljoin(self._base_url, endpoint.lstrip('/'))` — a relative reference against a no-trailing-slash base, silently dropping `api_base` under RFC 3986. Fixed:

```python
url = f"{self._base_url.rstrip('/')}/{endpoint.lstrip('/')}"
```

**Mechanism 2** (`validate_connection_async`'s SCIM health check): `urljoin(self._base_url, "/ServiceProviderConfig")` — here the *second* argument is itself absolute (starts with `/`), which makes `urljoin` replace the whole path regardless of trailing slash, dropping `api_base` a different way. `ServiceProviderConfig` is a standard SCIM endpoint under the SCIM service root, not the host root, so this needed the same fix, not just a trailing-slash tweak:

```python
sp_url = f"{self._base_url.rstrip('/')}/ServiceProviderConfig"
```

Both are documented in more depth in [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction, which also explains why plain `urljoin(host, "/health")` (used by the other `sol-*` packages' health checks, hitting the host root deliberately) is *not* the same bug — that one is an intentional absolute-path replacement, this package's `ServiceProviderConfig` check was not meant to be.

## Testing design

`tests/test_base.py` opens with the private-dependency stub this package's `requirements-dev.txt` makes necessary:

```python
if "sasci360apicore.encryption" not in sys.modules:
    _fake_core = types.ModuleType("sasci360apicore")
    _fake_encryption_mod = types.ModuleType("sasci360apicore.encryption")
    _fake_encryption_mod.Encryption = MagicMock(name="Encryption")
    _fake_core.encryption = _fake_encryption_mod
    sys.modules.setdefault("sasci360apicore", _fake_core)
    sys.modules.setdefault("sasci360apicore.encryption", _fake_encryption_mod)
```

`setdefault` means a real, actually-installed `api-core` (e.g. in an environment wired up to a private package index) is never shadowed — this only stubs the module when nothing real is already there. This is the pattern this repository points to as the reference example whenever a package needs to test against a dependency that can't or shouldn't be installed for CI (see `sol-content-delivery`'s DDD for the earlier, module-level-import-guard variant, and `sas-ci360-solutions`'/`sas-ci360-plan-connector`'s own docs for where this same technique was reused for pywin32 and cloud SDKs respectively).

## CI/CD pipeline

Same as every package in this repository.
