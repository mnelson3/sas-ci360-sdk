# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Execute Module

> **Status: canonical.** This is the actively maintained client for the Marketing Execution API.

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Execute module provides `CI360ExecuteBase`, a REST client for CI360's Marketing Execution API — campaign execution, batch jobs, job scheduling, and execution metrics — with both synchronous and asynchronous methods for every operation.

### Features

- JWT-based authentication
- Synchronous and asynchronous HTTP methods for every API operation
- Automatic retries with backoff for transient failures (429/5xx)
- Campaign execution, execution status, and cancellation
- Batch job submission, status, and cancellation
- Job scheduling (create, list, update, delete)
- Execution metrics
- Typed exception hierarchy for auth, connection, and validation errors

### Prerequisites

- Python 3.8+
- Access to a SAS Customer Intelligence 360 environment (host, tenant ID, and a shared secret or key configured for JWT signing)

This package depends on `sasci360apicore` from this same monorepo (pulled automatically via `requirements.txt`, no separate install or SAS administrator access needed) for JWT generation and retry-enabled HTTP transport.

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-execute
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Workflow, SCIM, etc.).

### Getting Started

```python
from sasci360solexecute.base import CI360ExecuteBase, CI360ExecuteConfig

config = CI360ExecuteConfig(
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

client = CI360ExecuteBase(config)

status = client.get_execution_status("execution-123")
```

### Troubleshooting

- Verify `host`, `secret_key`, and `tenant_id` are set correctly on `CI360ExecuteConfig` — these are required and initialization raises `CI360ExecuteValidationError` if any are missing.
- `host` must include the `https://` scheme for this package.
- Check `CI360ExecuteAuthError` / `CI360ExecuteConnectionError` messages for authentication vs. network failures.
- Enable `logging` at `INFO` level or below on the `sasci360solexecute.base.CI360ExecuteBase` logger to see connection and request activity.

## Developer/Implementation Guide

### Configuration

`CI360ExecuteConfig` is a dataclass holding connection and behavior settings:

```python
from sasci360solexecute.base import CI360ExecuteConfig

config = CI360ExecuteConfig(
    algorithm="HS256",          # JWT signing algorithm
    api_base="/marketingExecution",
    encoding="utf-8",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
    timeout=30,                 # per-request timeout, seconds
    max_retries=3,
    retry_backoff=0.5,
    enable_compression=True,
    batch_size=1000,
    max_concurrent_jobs=10,
    job_timeout=3600,
)
```

`host`, `secret_key`, and `tenant_id` are required; the client raises `CI360ExecuteValidationError` on construction if any are missing.

### Authentication

`CI360ExecuteBase` generates a JWT on initialization (via [PyJWT](https://pyjwt.readthedocs.io/)) and attaches it to every request:

```python
headers = client.get_auth_headers()
# {"Authorization": "Bearer ...", "Content-Type": "application/json", ...}
```

### Execution APIs

Every operation below has a synchronous method and an `_async` counterpart (e.g. `execute_campaign` / `execute_campaign_async`).

```python
# Campaign execution
client.execute_campaign(campaign_id, execution_params=None)
client.get_execution_status(execution_id)
client.cancel_execution(execution_id)

# Batch jobs
client.submit_batch_job(job_data)
client.get_batch_job_status(job_id)
client.cancel_batch_job(job_id)
client.get_batch_jobs(limit=50, offset=0, status_filter=None)

# Scheduling
client.schedule_job(schedule_data)
client.get_scheduled_jobs(limit=50, offset=0, active_only=True)
client.update_schedule(schedule_id, schedule_data)
client.delete_schedule(schedule_id)

# Metrics
client.get_execution_metrics(start_date=None, end_date=None, campaign_id=None)
```

#### Async usage

```python
import asyncio
from sasci360solexecute.base import CI360ExecuteBase, CI360ExecuteConfig

async def monitor_execution(client, execution_id):
    while True:
        status = await client.get_execution_status_async(execution_id)
        if status["status"] in ("completed", "failed", "cancelled"):
            return status
        await asyncio.sleep(10)

async def main():
    config = CI360ExecuteConfig(
        host="https://your-ci360-host.sas.com",
        secret_key="your-secret-key",
        tenant_id="your-tenant-id",
    )
    async with CI360ExecuteBase(config) as client:
        result = await client.execute_campaign_async("campaign-123")
        print(result)

asyncio.run(main())
```

### Error Handling

```python
from sasci360solexecute.base import (
    CI360ExecuteBase,
    CI360ExecuteAuthError,
    CI360ExecuteConnectionError,
    CI360ExecuteValidationError,
)

try:
    client = CI360ExecuteBase(config)
    status = client.get_execution_status("execution-123")
except CI360ExecuteValidationError as e:
    print(f"Invalid configuration: {e}")
except CI360ExecuteAuthError as e:
    print(f"Authentication failed: {e}")
except CI360ExecuteConnectionError as e:
    print(f"Connection error: {e}")
```

All of the above inherit from `CI360ExecuteError`, the base exception for the module.

### Testing

See [tests/test_base.py](tests/test_base.py) for the full test suite (100% line coverage on `base.py`). It mocks at the `requests.Session` boundary — the actual point this client makes HTTP calls — rather than a higher-level method, so the connection and URL-construction logic are exercised, not just the call wiring:

```python
from unittest.mock import MagicMock, patch
from sasci360solexecute.base import CI360ExecuteBase, CI360ExecuteConfig

@patch("sasci360solexecute.base.requests.Session")
def test_get_execution_status(mock_session_class):
    mock_session = MagicMock()
    mock_session.request.return_value.status_code = 200
    mock_session.request.return_value.json.return_value = {"status": "completed"}
    mock_session_class.return_value = mock_session

    config = CI360ExecuteConfig(host="https://api.example.com", secret_key="test-secret", tenant_id="test-tenant")
    client = CI360ExecuteBase(config)
    result = client.get_execution_status("execution-123")
    assert result["status"] == "completed"
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

For more information, see [Marketing Execution API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-mkt-exec.htm).
