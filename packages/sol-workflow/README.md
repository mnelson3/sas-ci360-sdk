# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Workflow Module

> **Status: canonical.** This is the actively maintained client for the Workflow API.

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Workflow module provides `CI360WorkflowBase`, a REST client for managing CI360 marketing workflows, process executions, triggers, and workflow templates, with both synchronous and asynchronous methods for every operation.

### Features

- JWT-based authentication
- Synchronous and asynchronous HTTP methods for every API operation
- Automatic retries with backoff for transient failures (429/5xx)
- Workflow, process, trigger, and template CRUD operations
- Context manager support (`with` / `async with`)
- Typed exception hierarchy for auth, connection, and validation errors

### Prerequisites

- Python 3.8+
- Access to a SAS Customer Intelligence 360 environment (host, tenant ID, and a shared secret or key configured for JWT signing)

This package depends on `sasci360apicore` from this same monorepo (pulled automatically via `requirements.txt`) for JWT generation and retry-enabled HTTP transport.

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-workflow
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Marketing Data, SCIM, etc.).

### Getting Started

```python
from sasci360solworkflow.base import CI360WorkflowBase, CI360WorkflowConfig

config = CI360WorkflowConfig(
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

client = CI360WorkflowBase(config)

workflows = client.get_workflows(limit=20)
```

### Troubleshooting

- Verify `host`, `secret_key`, and `tenant_id` are set correctly on `CI360WorkflowConfig` — these are required and initialization raises `CI360WorkflowValidationError` if any are missing.
- Check `CI360WorkflowAuthError` / `CI360WorkflowConnectionError` messages for authentication vs. network failures.
- Enable `logging` at `INFO` level or below on the `sasci360solworkflow.base.CI360WorkflowBase` logger to see connection and request activity.

## Developer/Implementation Guide

### Configuration

`CI360WorkflowConfig` is a dataclass holding connection and behavior settings:

```python
from sasci360solworkflow.base import CI360WorkflowConfig

config = CI360WorkflowConfig(
    algorithm="HS256",          # JWT signing algorithm
    api_base="/marketingWorkflow",
    encoding="utf-8",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
    timeout=30,                 # per-request timeout, seconds
    max_retries=3,
    retry_backoff=0.5,
    enable_compression=True,
    max_concurrent_workflows=50,
    workflow_timeout=7200,
)
```

`host`, `secret_key`, and `tenant_id` are required; the client raises `CI360WorkflowValidationError` on construction if any are missing, or if `algorithm` isn't one of `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`.

### Authentication

`CI360WorkflowBase` generates a JWT on initialization (via [PyJWT](https://pyjwt.readthedocs.io/)) and attaches it to every request:

```python
headers = client.get_auth_headers()
# {"Authorization": "Bearer ...", "Content-Type": "application/json", ...}
```

### Workflow, Process, Trigger, and Template APIs

Every operation below has a synchronous method and an `_async` counterpart (e.g. `get_workflows` / `get_workflows_async`).

```python
# Workflows
client.get_workflows(limit=50, offset=0, filters=None)
client.get_workflow(workflow_id)
client.create_workflow(workflow_data)
client.update_workflow(workflow_id, workflow_data)
client.delete_workflow(workflow_id)

# Process executions
client.start_process(workflow_id, input_data=None)
client.get_process_status(process_id)
client.cancel_process(process_id)
client.get_processes(limit=50, offset=0, status_filter=None)

# Triggers
client.get_triggers(limit=50, offset=0, filters=None)
client.create_trigger(trigger_data)
client.update_trigger(trigger_id, trigger_data)
client.delete_trigger(trigger_id)

# Templates
client.get_workflow_templates(category=None, limit=50, offset=0)
client.create_workflow_from_template(template_id, workflow_data)
```

#### Async usage

```python
import asyncio
from sasci360solworkflow.base import CI360WorkflowBase, CI360WorkflowConfig

async def monitor_process(client, workflow_id, input_data):
    process = await client.start_process_async(workflow_id, input_data)
    process_id = process["processId"]

    while True:
        status = await client.get_process_status_async(process_id)
        if status["status"] in ("completed", "failed", "cancelled"):
            return status
        await asyncio.sleep(10)

async def main():
    config = CI360WorkflowConfig(
        host="https://your-ci360-host.sas.com",
        secret_key="your-secret-key",
        tenant_id="your-tenant-id",
    )
    async with CI360WorkflowBase(config) as client:
        result = await monitor_process(client, "wf-123", {"customerId": "cust-123"})
        print(result)

asyncio.run(main())
```

### Error Handling

```python
from sasci360solworkflow.base import (
    CI360WorkflowBase,
    CI360WorkflowAuthError,
    CI360WorkflowConnectionError,
    CI360WorkflowValidationError,
)

try:
    client = CI360WorkflowBase(config)
    workflows = client.get_workflows()
except CI360WorkflowValidationError as e:
    print(f"Invalid configuration: {e}")
except CI360WorkflowAuthError as e:
    print(f"Authentication failed: {e}")
except CI360WorkflowConnectionError as e:
    print(f"Connection error: {e}")
```

All of the above inherit from `CI360WorkflowError`, the base exception for the module.

### Testing

See [tests/test_base.py](tests/test_base.py) for the full test suite (100% line coverage on `base.py`). It mocks at the `requests.Session` boundary — the actual point this client makes HTTP calls — rather than a higher-level method like `_make_request_async`, so the connection and URL-construction logic are exercised, not just the call wiring:

```python
from unittest.mock import MagicMock, patch
from sasci360solworkflow.base import CI360WorkflowBase, CI360WorkflowConfig

@patch("sasci360solworkflow.base.requests.Session")
def test_get_workflows(mock_session_class):
    mock_session = MagicMock()
    mock_session.request.return_value.status_code = 200
    mock_session.request.return_value.json.return_value = {"items": [], "total": 0}
    mock_session_class.return_value = mock_session

    config = CI360WorkflowConfig(host="https://api.example.com", secret_key="test-secret", tenant_id="test-tenant")
    client = CI360WorkflowBase(config)
    result = client.get_workflows(limit=20)
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

For more information, see [Workflow API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-workflow.htm).
