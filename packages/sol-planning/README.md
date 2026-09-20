# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Planning Module

> **Status: canonical.** This is the actively maintained client for the Plan API.

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Planning module provides `CI360PlanningBase`, a REST client for CI360's Plan API — campaigns, audiences, audience size estimation, campaign optimization, analytics, and campaign templates — with both synchronous and asynchronous methods for every operation.

### Features

- JWT-based authentication
- Synchronous and asynchronous HTTP methods for every API operation
- Automatic retries with backoff for transient failures (429/5xx)
- Campaign CRUD and campaign optimization
- Audience CRUD and audience size estimation
- Campaign analytics
- Campaign template listing and template-based campaign creation
- Typed exception hierarchy for auth, connection, and validation errors

### Prerequisites

- Python 3.8+
- Access to a SAS Customer Intelligence 360 environment (host, tenant ID, and a shared secret or key configured for JWT signing)

This package depends on `sasci360apicore` from this same monorepo (pulled automatically via `requirements.txt`) for JWT generation and retry-enabled HTTP transport.

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-planning
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Workflow, SCIM, etc.).

### Getting Started

```python
from sasci360solplanning.base import CI360PlanningBase, CI360PlanningConfig

config = CI360PlanningConfig(
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

client = CI360PlanningBase(config)

campaigns = client.get_campaigns(limit=20)
```

### Troubleshooting

- Verify `host`, `secret_key`, and `tenant_id` are set correctly on `CI360PlanningConfig` — these are required and initialization raises `CI360PlanningValidationError` if any are missing.
- `host` must include the `https://` scheme for this package.
- Check `CI360PlanningAuthError` / `CI360PlanningConnectionError` messages for authentication vs. network failures.
- Enable `logging` at `INFO` level or below on the `sasci360solplanning.base.CI360PlanningBase` logger to see connection and request activity.

## Developer/Implementation Guide

### Configuration

`CI360PlanningConfig` is a dataclass holding connection and behavior settings:

```python
from sasci360solplanning.base import CI360PlanningConfig

config = CI360PlanningConfig(
    algorithm="HS256",          # JWT signing algorithm
    api_base="/marketingPlanning",
    encoding="utf-8",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
    timeout=30,                 # per-request timeout, seconds
    max_retries=3,
    retry_backoff=0.5,
    enable_compression=True,
    max_campaigns_per_user=100,
    max_audience_size=1000000,
)
```

`host`, `secret_key`, and `tenant_id` are required; the client raises `CI360PlanningValidationError` on construction if any are missing.

### Authentication

`CI360PlanningBase` generates a JWT on initialization (via [PyJWT](https://pyjwt.readthedocs.io/)) and attaches it to every request:

```python
headers = client.get_auth_headers()
# {"Authorization": "Bearer ...", "Content-Type": "application/json", ...}
```

### Planning APIs

Every operation below has a synchronous method and an `_async` counterpart (e.g. `get_campaigns` / `get_campaigns_async`).

```python
# Campaigns
client.get_campaigns(limit=50, offset=0, filters=None)
client.get_campaign(campaign_id)
client.create_campaign(campaign_data)
client.update_campaign(campaign_id, campaign_data)
client.delete_campaign(campaign_id)
client.optimize_campaign(campaign_id, optimization_params=None)

# Audiences
client.get_audiences(limit=50, offset=0, filters=None)
client.get_audience(audience_id)
client.create_audience(audience_data)
client.update_audience(audience_id, audience_data)
client.delete_audience(audience_id)
client.estimate_audience_size(audience_criteria)

# Analytics and templates
client.get_campaign_analytics(campaign_id, start_date=None, end_date=None)
client.get_campaign_templates(category=None, limit=50, offset=0)
client.create_campaign_from_template(template_id, campaign_data)
```

#### Async usage

```python
import asyncio
from sasci360solplanning.base import CI360PlanningBase, CI360PlanningConfig

async def main():
    config = CI360PlanningConfig(
        host="https://your-ci360-host.sas.com",
        secret_key="your-secret-key",
        tenant_id="your-tenant-id",
    )
    async with CI360PlanningBase(config) as client:
        campaign = await client.create_campaign_async({"name": "Q4 Promo"})
        print(campaign)

asyncio.run(main())
```

### Error Handling

```python
from sasci360solplanning.base import (
    CI360PlanningBase,
    CI360PlanningAuthError,
    CI360PlanningConnectionError,
    CI360PlanningValidationError,
)

try:
    client = CI360PlanningBase(config)
    campaigns = client.get_campaigns()
except CI360PlanningValidationError as e:
    print(f"Invalid configuration: {e}")
except CI360PlanningAuthError as e:
    print(f"Authentication failed: {e}")
except CI360PlanningConnectionError as e:
    print(f"Connection error: {e}")
```

All of the above inherit from `CI360PlanningError`, the base exception for the module.

### Testing

See [tests/test_base.py](tests/test_base.py) for the full test suite (100% line coverage on `base.py`). It mocks at the `requests.Session` boundary — the actual point this client makes HTTP calls — rather than a higher-level method, so the connection and URL-construction logic are exercised, not just the call wiring:

```python
from unittest.mock import MagicMock, patch
from sasci360solplanning.base import CI360PlanningBase, CI360PlanningConfig

@patch("sasci360solplanning.base.requests.Session")
def test_get_campaigns(mock_session_class):
    mock_session = MagicMock()
    mock_session.request.return_value.status_code = 200
    mock_session.request.return_value.json.return_value = {"items": [], "total": 0}
    mock_session_class.return_value = mock_session

    config = CI360PlanningConfig(host="https://api.example.com", secret_key="test-secret", tenant_id="test-tenant")
    client = CI360PlanningBase(config)
    result = client.get_campaigns(limit=20)
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

For more information, see [Plan API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-plan.htm).
