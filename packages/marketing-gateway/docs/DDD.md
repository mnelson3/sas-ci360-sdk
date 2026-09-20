# Detailed Design Document — sasci360apimarketinggateway

| | |
| --- | --- |
| Document | DDD-MARKETINGGATEWAY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/marketing-gateway` (`sasci360apimarketinggateway`) |

## Architecture

This package is Layer 2 like its 6 `sol-*` siblings, but from an older client generation — no `Config` dataclass, no shared `…Base` class across resources. Instead:

```
Base(algorithm, api, encoding, host, secret_key, tenant_id)
  ├── generates its own JWT via api-core's Encryption
  ├── holds an api-core Connection instance
  └── is subclassed by:
        Root, Agents, Configuration, DataDownload, Events
```

Each subclass owns its own endpoints and builds its own request manually (headers, action, URL) rather than going through a shared `_make_request_async`/`_make_request` pair — see `root/__init__.py`'s `get_root()` as the representative example:

```python
class Root(Base):
    def get_root(self) -> requests.Response:
        token = self.token
        headers = {"Content-Type": "application/json", "Authorization": "Bearer {0}".format(token)}
        url = "https://{0}{1}{2}".format(self.host, self.api, "/")
        return self.connection.connect(action="GET", data=None, headers=headers, params=None, url=url)
```

## `host` is a bare hostname here, not a full URL

Unlike every `sol-*` package (whose `Config.host` must include the `https://` scheme, since their `_make_request_async` doesn't add one), this package's `url = "https://{0}{1}{2}".format(host, api, api_path)` builds the scheme itself. Passing a `sol-*`-style `host="https://..."` here would produce a doubled/broken URL. This is a genuine, historical convention difference between the two client generations, not a bug in either — see [sas-ci360-sdk/IMPLEMENTER_GUIDE.md](../../../IMPLEMENTER_GUIDE.md) §3 for how the UAT harness (`tests/TestLiveTenant.py`) and the implementer guide both call this out explicitly so it isn't a trap.

## The malformed install_requires fix

Identical defect and fix to `api-core`'s — see [api-core's DDD.md](../../api-core/docs/DDD.md) §The malformed install_requires fix for the full before/after. This package's version additionally declares `sasci360apicore~=0.0.1` in its corrected `install_requires`, since (unlike `api-core` itself) it has a real dependency on that package.

## Testing design

`tests/TestRoot.py` is the representative example: patches `requests.get` directly (this generation predates the `Session`-object pattern), asserts on the constructed URL, headers, and the parsed JSON result. `tests/TestLiveTenant.py` (added 2026-09-20) follows the same `unittest.TestCase` convention rather than the pytest-function style the `sol-*` packages' live-tenant tests use, for consistency with this package's own existing test suite.

## CI/CD pipeline

Same as every package in this repository.
