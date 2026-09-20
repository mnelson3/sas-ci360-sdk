# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Identity Module

> **Status: canonical.** This is the actively maintained client for the SCIM API.

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Identity module provides `CI360IdentityBase`, a REST client for CI360's SCIM API — user and group CRUD, SCIM patch, authentication, token validation/refresh, service-provider config, and bulk operations — with both synchronous and asynchronous methods for every operation.

### Features

- JWT-based authentication
- Synchronous and asynchronous HTTP methods for every API operation
- Automatic retries with backoff for transient failures (429/5xx)
- User and group CRUD, plus SCIM `PATCH`
- Token authentication, validation, and refresh
- Service-provider config lookup and bulk SCIM operations
- Typed exception hierarchy for auth, connection, and validation errors

### Prerequisites

- Python 3.8+
- Access to a SAS Customer Intelligence 360 environment (host, tenant ID, and a shared secret or key configured for JWT signing)

This package depends on `sasci360apicore` from this same monorepo (pulled automatically via `requirements.txt`, no private package index or separate access needed) for JWT generation and retry-enabled HTTP transport.

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-identity
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Workflow, Marketing Data, etc.).

### Getting Started

```python
from sasci360solidentity.base import CI360IdentityBase, CI360IdentityConfig

config = CI360IdentityConfig(
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

client = CI360IdentityBase(config)

users = client.get_users(limit=20)
```

### Troubleshooting

- Verify `host`, `secret_key`, and `tenant_id` are set correctly on `CI360IdentityConfig` — these are required and initialization raises `CI360IdentityValidationError` if any are missing.
- `host` must include the `https://` scheme for this package.
- Check `CI360IdentityAuthError` / `CI360IdentityConnectionError` messages for authentication vs. network failures.
- Enable `logging` at `INFO` level or below on the `sasci360solidentity.base.CI360IdentityBase` logger to see connection and request activity.

## Developer/Implementation Guide

### Configuration

`CI360IdentityConfig` is a dataclass holding connection and behavior settings:

```python
from sasci360solidentity.base import CI360IdentityConfig

config = CI360IdentityConfig(
    algorithm="HS256",          # JWT signing algorithm
    api_base="/scim",
    encoding="utf-8",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
    timeout=30,                 # per-request timeout, seconds
    max_retries=3,
    retry_backoff=0.5,
    enable_compression=True,
    scim_version="2.0",
)
```

`host`, `secret_key`, and `tenant_id` are required; the client raises `CI360IdentityValidationError` on construction if any are missing.

### Authentication

`CI360IdentityBase` generates a JWT on initialization (via [PyJWT](https://pyjwt.readthedocs.io/)) and attaches it to every request:

```python
headers = client.get_auth_headers()
# {"Authorization": "Bearer ...", "Content-Type": "application/json", ...}
```

### Identity (SCIM) APIs

Every operation below has a synchronous method and an `_async` counterpart (e.g. `get_users` / `get_users_async`).

```python
# Users
client.get_users(limit=100, offset=0, filters=None)
client.get_user(user_id)
client.create_user(user_data)
client.update_user(user_id, user_data)
client.patch_user(user_id, patch_data)
client.delete_user(user_id)

# Groups
client.get_groups(limit=100, offset=0, filters=None)
client.get_group(group_id)
client.create_group(group_data)
client.update_group(group_id, group_data)
client.delete_group(group_id)

# Auth / tokens / service-provider config
client.authenticate_user(credentials)
client.validate_token(token)
client.refresh_token(refresh_token)
client.get_service_provider_config()

# Bulk
client.bulk_operation(operations)
```

#### Async usage

```python
import asyncio
from sasci360solidentity.base import CI360IdentityBase, CI360IdentityConfig

async def main():
    config = CI360IdentityConfig(
        host="https://your-ci360-host.sas.com",
        secret_key="your-secret-key",
        tenant_id="your-tenant-id",
    )
    async with CI360IdentityBase(config) as client:
        user = await client.get_user_async("user-123")
        print(user)

asyncio.run(main())
```

### Error Handling

```python
from sasci360solidentity.base import (
    CI360IdentityBase,
    CI360IdentityAuthError,
    CI360IdentityConnectionError,
    CI360IdentityValidationError,
)

try:
    client = CI360IdentityBase(config)
    users = client.get_users()
except CI360IdentityValidationError as e:
    print(f"Invalid configuration: {e}")
except CI360IdentityAuthError as e:
    print(f"Authentication failed: {e}")
except CI360IdentityConnectionError as e:
    print(f"Connection error: {e}")
```

All of the above inherit from `CI360IdentityError`, the base exception for the module.

### Testing

See [tests/test_base.py](tests/test_base.py) for the full test suite (100% line coverage on `base.py`). It mocks at the `requests.Session` boundary — the actual point this client makes HTTP calls — rather than a higher-level method, so the connection and URL-construction logic are exercised, not just the call wiring:

```python
from unittest.mock import MagicMock, patch
from sasci360solidentity.base import CI360IdentityBase, CI360IdentityConfig

@patch("sasci360solidentity.base.requests.Session")
def test_get_users(mock_session_class):
    mock_session = MagicMock()
    mock_session.request.return_value.status_code = 200
    mock_session.request.return_value.json.return_value = {"Resources": [], "totalResults": 0}
    mock_session_class.return_value = mock_session

    config = CI360IdentityConfig(host="https://api.example.com", secret_key="test-secret", tenant_id="test-tenant")
    client = CI360IdentityBase(config)
    result = client.get_users(limit=20)
    assert result["totalResults"] == 0
```

Run the suite with:
```bash
pytest tests/
```

`tests/test_live_tenant.py` runs the same operations against a real tenant, skipped (not failed) unless `CI360_HOST`, `CI360_SECRET_KEY`, and `CI360_TENANT_ID` are set — see [`UAT.md`](../../UAT.md) in the repo root.

### Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md). Scope a pull request to the package(s) it actually changes, and run this package's own test suite before submitting.

### License

This project is licensed under the [Nelson Grey LLC Community License 1.0](../../LICENSE).

- **Free for individuals, education, and research**: use, modify, and distribute this software for non-commercial purposes
- **Commercial evaluation**: evaluate the software for a possible commercial use, free of charge
- **Commercial production use**: requires a commercial license from Nelson Grey LLC
- **Automatic conversion**: on December 13, 2029, this automatically converts to the Apache License 2.0

For commercial licensing inquiries, contact support@nelsongrey.com.

### Additional Resources

For more information, see [SCIM API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-scim.htm).
