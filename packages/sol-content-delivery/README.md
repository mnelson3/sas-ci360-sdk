# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Content Delivery Module

> **Status: canonical.** This is the actively maintained client for the Digital Assets API.

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Content Delivery module provides `CI360ContentDeliveryBase`, a REST client for CI360's Digital Assets API — asset CRUD, content delivery and delivery status, content templates, and content analytics — with both synchronous and asynchronous methods for every operation.

### Features

- JWT-based authentication
- Synchronous and asynchronous HTTP methods for every API operation
- Automatic retries with backoff for transient failures (429/5xx)
- Digital asset CRUD and file upload
- Content delivery triggering and delivery-status polling
- Content template listing and template-based content creation
- Content delivery analytics
- Typed exception hierarchy for auth, connection, and validation errors

### Prerequisites

- Python 3.8+
- Access to a SAS Customer Intelligence 360 environment (host, tenant ID, and a shared secret or key configured for JWT signing)

This package depends on `sasci360apicore` and `requests-toolbelt` (pulled automatically via `requirements.txt`) — `requests-toolbelt` is used for multipart asset uploads.

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-content-delivery
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Workflow, SCIM, etc.).

### Getting Started

```python
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase, CI360ContentDeliveryConfig

config = CI360ContentDeliveryConfig(
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

client = CI360ContentDeliveryBase(config)

assets = client.get_assets(limit=20)
```

### Troubleshooting

- Verify `host`, `secret_key`, and `tenant_id` are set correctly on `CI360ContentDeliveryConfig` — these are required and initialization raises `CI360ContentDeliveryValidationError` if any are missing.
- `host` must include the `https://` scheme for this package.
- Check `CI360ContentDeliveryAuthError` / `CI360ContentDeliveryConnectionError` messages for authentication vs. network failures.
- Enable `logging` at `INFO` level or below on the `sasci360solcontentdelivery.base.CI360ContentDeliveryBase` logger to see connection and request activity.

## Developer/Implementation Guide

### Configuration

`CI360ContentDeliveryConfig` is a dataclass holding connection and behavior settings:

```python
from sasci360solcontentdelivery.base import CI360ContentDeliveryConfig

config = CI360ContentDeliveryConfig(
    algorithm="HS256",          # JWT signing algorithm
    api_base="/digital-assets",
    encoding="utf-8",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
    timeout=30,                 # per-request timeout, seconds
    max_retries=3,
    retry_backoff=0.5,
    enable_compression=True,
    max_file_size_mb=100,
    supported_formats=["jpg", "jpeg", "png", "gif", "pdf", "html", "txt", "mp4", "avi"],
)
```

`host`, `secret_key`, and `tenant_id` are required; the client raises `CI360ContentDeliveryValidationError` on construction if any are missing.

### Authentication

`CI360ContentDeliveryBase` generates a JWT on initialization (via [PyJWT](https://pyjwt.readthedocs.io/)) and attaches it to every request:

```python
headers = client.get_auth_headers()
# {"Authorization": "Bearer ...", "Content-Type": "application/json", ...}
```

### Content Delivery APIs

Every operation below has a synchronous method and an `_async` counterpart (e.g. `get_assets` / `get_assets_async`).

```python
# Assets
client.get_assets(limit=50, offset=0, filters=None)
client.get_asset(asset_id)
client.upload_asset(asset_data, file_content, filename)
client.update_asset(asset_id, asset_data)
client.delete_asset(asset_id)

# Delivery
client.deliver_content(asset_id, delivery_config)
client.get_delivery_status(delivery_id)
client.get_deliveries(limit=50, offset=0, status_filter=None)

# Templates
client.get_content_templates(category=None, limit=50, offset=0)
client.create_content_from_template(template_id, content_data)

# Analytics
client.get_content_analytics(asset_id=None, start_date=None, end_date=None)
```

#### Async usage

```python
import asyncio
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase, CI360ContentDeliveryConfig

async def main():
    config = CI360ContentDeliveryConfig(
        host="https://your-ci360-host.sas.com",
        secret_key="your-secret-key",
        tenant_id="your-tenant-id",
    )
    async with CI360ContentDeliveryBase(config) as client:
        with open("banner.png", "rb") as f:
            asset = await client.upload_asset_async({"name": "banner"}, f.read(), "banner.png")
        print(asset)

asyncio.run(main())
```

### Error Handling

```python
from sasci360solcontentdelivery.base import (
    CI360ContentDeliveryBase,
    CI360ContentDeliveryAuthError,
    CI360ContentDeliveryConnectionError,
    CI360ContentDeliveryValidationError,
)

try:
    client = CI360ContentDeliveryBase(config)
    assets = client.get_assets()
except CI360ContentDeliveryValidationError as e:
    print(f"Invalid configuration: {e}")
except CI360ContentDeliveryAuthError as e:
    print(f"Authentication failed: {e}")
except CI360ContentDeliveryConnectionError as e:
    print(f"Connection error: {e}")
```

All of the above inherit from `CI360ContentDeliveryError`, the base exception for the module.

### Testing

See [tests/test_base.py](tests/test_base.py) for the full test suite (100% line coverage on `base.py`). It mocks at the `requests.Session` boundary — the actual point this client makes HTTP calls — rather than a higher-level method, so the connection and URL-construction logic are exercised, not just the call wiring:

```python
from unittest.mock import MagicMock, patch
from sasci360solcontentdelivery.base import CI360ContentDeliveryBase, CI360ContentDeliveryConfig

@patch("sasci360solcontentdelivery.base.requests.Session")
def test_get_assets(mock_session_class):
    mock_session = MagicMock()
    mock_session.request.return_value.status_code = 200
    mock_session.request.return_value.json.return_value = {"items": [], "total": 0}
    mock_session_class.return_value = mock_session

    config = CI360ContentDeliveryConfig(host="https://api.example.com", secret_key="test-secret", tenant_id="test-tenant")
    client = CI360ContentDeliveryBase(config)
    result = client.get_assets(limit=20)
    assert result["total"] == 0
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

For more information, see [Digital Assets API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-digital-assets.htm).
