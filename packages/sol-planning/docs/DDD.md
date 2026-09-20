# Detailed Design Document — sasci360solplanning

| | |
| --- | --- |
| Document | DDD-SOLPLANNING-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-planning` (`sasci360solplanning`) |

## Architecture

Standard Layer-2 domain-client pattern — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md). Exception hierarchy: `CI360PlanningError`, `CI360PlanningAuthError`, `CI360PlanningConnectionError`, `CI360PlanningValidationError`.

## History: this package's fixes predate the rest of the family's testing pass

Both defects below were found and fixed during the monorepo migration itself (2026-09-20, earlier the same day as the broader testing pass covered in the parent repo's DDD.md), independently of the systematic `sol-*` review that later found the same URL-construction defect in `sol-data`, `sol-execute`, `sol-workflow`, and `sol-identity`. This package's fixes are what that later review used as the template.

## The JWT auth bug

`_generate_token()` previously generated its own JWT locally with the wrong payload shape and an unencoded signing key, rather than delegating to `api-core`'s `Encryption` class. Fixed (commit `22b9a82`) to match the pattern every other client uses:

```python
try:
    from sasci360apicore.encryption import Encryption
except ImportError:
    Encryption = None

def _generate_token(self) -> str:
    if Encryption is None:
        raise CI360PlanningAuthError(...)
    ...
```

## The api_base URL bug

`_make_request_async` used `urljoin(str(self.config.host) + self.config.api_base, endpoint.lstrip('/'))`. Fixed (commit `4105e81`) to:

```python
url = f"{str(self.config.host).rstrip('/')}{self.config.api_base}/{endpoint.lstrip('/')}"
```

Every existing test at the time mocked `_make_request_async` itself, so none of them exercised the URL it built — which is exactly how this went undetected. The fix's regression test, `test_make_request_async_includes_api_base_in_url`, mocks one level deeper (`session.request` directly) specifically to close that gap; see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction for the fuller explanation this package's finding led to.

## Testing design

Same conventions as the other `sol-*` packages, with the one dedicated URL-construction regression test noted above. This package's `base.py` sits at 65% line coverage as of 2026-09-20 — the two real defects above are fixed and regression-tested, but the broader "test every branch at the session boundary" pass done for `sol-data`/`sol-execute`/`sol-workflow`/`sol-identity`/`sol-content-delivery` wasn't repeated here in the same session. Closing that gap is a natural next step, following the exact template those five packages now provide.

## CI/CD pipeline

Same as every package in this repository.
