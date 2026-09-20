# Detailed Design Document — sasci360solworkflow

| | |
| --- | --- |
| Document | DDD-SOLWORKFLOW-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-workflow` (`sasci360solworkflow`) |

## Architecture

Standard Layer-2 domain-client pattern — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md). Exception hierarchy: `CI360WorkflowError`, `CI360WorkflowAuthError`, `CI360WorkflowConnectionError`, `CI360WorkflowValidationError`.

## The JWT auth bug (found during the monorepo migration)

`_generate_token()` before the fix generated its own JWT locally rather than delegating to `api-core`'s `Encryption` class — with the wrong payload shape and an unencoded signing key. CI360 would have rejected every real request this client made, despite the package's own mocked unit tests passing (the tests mocked the encryption step itself, so the defect was invisible to them). Fixed to match the pattern `sol-data`/`sol-execute`/`sol-identity`/`sol-content-delivery`/`sol-planning` already used:

```python
try:
    from sasci360apicore.encryption import Encryption
except ImportError:  # pragma: no cover - optional dependency, only needed at runtime
    Encryption = None

def _generate_token(self) -> str:
    if Encryption is None:
        raise CI360WorkflowAuthError("sasci360apicore is required to generate authentication tokens")
    try:
        encryption = Encryption(algorithm=self.config.algorithm, encoding=self.config.encoding)
        return encryption.generate_jwt(tenant_id=self.config.tenant_id, secret_key=self.config.secret_key)
    except Exception as e:
        raise CI360WorkflowAuthError(f"Failed to generate authentication token: {e}")
```

## The api_base URL bug

Same defect and fix as documented in [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction — `_make_request_async` used `urljoin(host + api_base, endpoint)`, dropping `/marketingWorkflow` from every real request. Fixed with plain string formatting.

## Testing design

`tests/test_base.py` mocks the `session.get`/`session.request` boundary directly for connection-validation and `_make_request_async` tests. `Encryption` is patched at `sasci360solworkflow.base.Encryption` (a module-level name, since this package uses the try/except-guarded import pattern) rather than at `sasci360apicore.encryption.Encryption` (which is the pattern `sol-content-delivery`/`sol-identity` use, since those do a lazy import inside the method instead).

## CI/CD pipeline

Same as every package in this repository.
