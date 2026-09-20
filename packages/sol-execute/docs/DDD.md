# Detailed Design Document — sasci360solexecute

| | |
| --- | --- |
| Document | DDD-SOLEXECUTE-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-execute` (`sasci360solexecute`) |

## Architecture

Standard Layer-2 domain-client pattern — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md). Exception hierarchy: `CI360ExecuteError`, `CI360ExecuteAuthError`, `CI360ExecuteConnectionError`, `CI360ExecuteValidationError`.

## The api_base URL bug

Same defect and fix as documented in [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction — `_make_request_async` used `urljoin(host + api_base, endpoint)`, dropping `/marketingExecution` from every real request. Fixed with plain string formatting:

```python
host = self.config.host or ""
url = f"{host.rstrip('/')}{self.config.api_base}/{endpoint.lstrip('/')}"
```

(This package's `host` handling defaults to `""` rather than asserting non-None, unlike `sol-data`/`sol-workflow`/`sol-identity` — a minor stylistic difference between packages, not a functional one, since `_validate_config()` already guarantees `host` is set before this code path runs.)

## Testing design

`tests/test_base.py` mocks the `session.get`/`session.request` boundary directly for connection-validation and `_make_request_async` tests, following the pattern established across this repository on 2026-09-20 — see [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md) §9 for why that boundary matters more than it looks like it should.

## CI/CD pipeline

Same as every package in this repository.
