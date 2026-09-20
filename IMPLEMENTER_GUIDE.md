# Implementer Guide — sas-ci360-sdk

A practical walkthrough for building a CI360 integration on these packages. For requirements and design rationale, see [`docs/`](docs/); this guide is about actually writing code.

## 1. Get an Access Point

In the CI360 UI: **General Settings → External Access → Access Points**. Create one and note the three values it gives you:

- **host** — e.g. `extapigwservice-prod.ci360.sas.com`
- **tenant ID**
- **client secret**

Nothing else is needed to authenticate. Never commit these — see §5.

## 2. Install just what you need

Each package is independent. If you only need Marketing Data:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-data
pip install -r requirements.txt
pip install -e .
```

If you need more than one API, repeat for each package — installing `sol-workflow` doesn't pull in `sol-identity`'s dependencies, and vice versa.

## 3. Your first authenticated call

```python
from sasci360soldata.base import CI360DataBase, CI360DataConfig

config = CI360DataConfig(
    host="https://extapigwservice-prod.ci360.sas.com",   # full https:// URL for sol-* packages
    secret_key="your-client-secret",
    tenant_id="your-tenant-id",
)
client = CI360DataBase(config)

if client.validate_connection():
    tables = client.get_tables(limit=10)
    print(tables)
```

Every `sol-*` package follows this exact shape — swap the import and config/class names per the table in the root `README.md`. `marketing-gateway` is the one exception (an older generation): see `packages/marketing-gateway/README.md`.

**One gotcha worth knowing about**: `sol-*` packages need `host` to include the `https://` scheme. `marketing-gateway`'s `Root` class needs a bare hostname instead (it builds the `https://` prefix itself). If you're setting `CI360_HOST` as an environment variable across multiple packages, see `UAT.md` for how the live-tenant tests handle this.

## 4. Sync vs. async

Every method has both forms — `get_tables()` (sync) and `get_tables_async()` (async), the sync path wraps the async one in `asyncio.run()`. Use whichever fits your caller; there's no functional difference, and no need to run an event loop yourself unless you're already async.

```python
import asyncio

async def main():
    result = await client.get_tables_async(limit=10)
    print(result)

asyncio.run(main())
```

## 5. Handling credentials

Never hardcode a secret or commit a real tenant ID. The pattern every package's tests use:

```bash
export CI360_HOST="extapigwservice-prod.ci360.sas.com"
export CI360_SECRET_KEY="..."
export CI360_TENANT_ID="..."
```

```python
import os
from sasci360soldata.base import CI360DataConfig

config = CI360DataConfig(
    host="https://" + os.environ["CI360_HOST"],
    secret_key=os.environ["CI360_SECRET_KEY"],
    tenant_id=os.environ["CI360_TENANT_ID"],
)
```

For a real deployment, source these from your own secret store (see `sas-ci360-plan-connector`'s cloud `SecretProvider` pattern for one example per major cloud) rather than plain environment variables.

## 6. Handling errors

Every package raises a typed exception hierarchy: `CI360<Domain>Error` (base), `…AuthError` (bad credentials or expired token), `…ConnectionError` (network failure, 5xx, or "couldn't establish a connection at all"), `…ValidationError` (bad config or bad arguments). Catch the specific one you can actually do something about:

```python
from sasci360soldata.base import CI360DataAuthError, CI360DataConnectionError

try:
    result = client.get_tables()
except CI360DataAuthError:
    # credentials are wrong or the tenant rejected the token - don't retry blindly
    raise
except CI360DataConnectionError:
    # transient - the client already retried 429/500/502/503/504 internally;
    # this means it gave up, so back off longer before trying again yourself
    raise
```

Retry on 429/500/502/503/504 already happens inside the client (`NFR-1`, `Retry`-mounted `HTTPAdapter`) — you don't need to implement your own retry loop for those.

## 7. Composing multiple clients

Nothing in this repository stops you from using several packages together in one process — that's exactly what `sas-ci360-solutions` does (see its own `IMPLEMENTER_GUIDE.md` for the identity-bridge cycle as a worked example: it composes `sol-data`'s import-request-job endpoints with SCIM-side identity records and the Marketing Gateway's file upload). The rule of thumb: compose Layer 2 clients, don't reimplement their HTTP or auth logic.

## 8. Testing your own code against this SDK

- **Unit test your code the same way these packages test themselves**: mock at the `session.get`/`session.request` boundary (via `unittest.mock.patch('yourmodule.requests.Session')` or similar), not at a higher-level wrapper — see `docs/TRD.md` §9 for why that distinction matters. Every package's own `tests/test_base.py` is a working example to copy the pattern from.
- **Verify against a real tenant before shipping.** Each package's `tests/test_live_tenant.py` is both a working example and something you can literally run yourself: `CI360_HOST=... CI360_SECRET_KEY=... CI360_TENANT_ID=... pytest packages/sol-data/tests/test_live_tenant.py -v`. See [`UAT.md`](UAT.md).

## 9. Extending a client

If CI360 adds an endpoint a package doesn't cover yet, add a method to that package's `base.py` following the existing shape (one async method calling `self._make_request_async`, one sync wrapper calling `self._make_request`), then add both a mocked unit test (session-boundary) and, if it's a read-only endpoint, a live-tenant test. Don't reimplement `_make_request_async`/`_make_request` — every endpoint should go through them so retry, auth, and error-mapping stay centralized.

## 10. Common pitfalls

- **Don't use `urljoin` for building request URLs.** See `docs/DDD.md`'s URL-construction section — it silently drops `api_base` under common conditions. Plain string formatting is correct here.
- **Don't mock `_make_request_async` when testing connection/URL logic.** It hides exactly the layer you're trying to verify.
- **Don't assume `marketing-gateway`'s `host` format matches the `sol-*` packages'.** See §3.
