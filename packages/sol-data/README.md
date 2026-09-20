# SAS Customer Intelligence 360

## SAS 360 SOLUTIONS - Data Module

> **Status: canonical.** This is the actively maintained client for the Marketing Data API.

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Data module provides `CI360DataBase`, a REST client for CI360's Marketing Data API — customers, segments, import/export, schema, import request jobs, file transfer, and tables — with both synchronous and asynchronous methods for every operation.

### Features

- JWT-based authentication
- Synchronous and asynchronous HTTP methods for every API operation
- Automatic retries with backoff for transient failures (429/5xx)
- Customer and segment CRUD, data import/export/validation, schema read/update
- Import request job creation and polling, signed-URL file transfer and upload
- Table CRUD
- Typed exception hierarchy for auth, connection, and validation errors

### Prerequisites

- Python 3.8+
- Access to a SAS Customer Intelligence 360 environment (host, tenant ID, and a shared secret or key configured for JWT signing)

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-data
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Workflow, SCIM, etc.).

### Getting Started

```python
from sasci360soldata.base import CI360DataBase, CI360DataConfig

config = CI360DataConfig(
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

client = CI360DataBase(config)

customers = client.get_customers(limit=20)
```

### Troubleshooting

- Verify `host`, `secret_key`, and `tenant_id` are set correctly on `CI360DataConfig` — these are required and initialization raises `CI360DataValidationError` if any are missing.
- `host` must include the `https://` scheme for this package.
- Check `CI360DataAuthError` / `CI360DataConnectionError` messages for authentication vs. network failures.
- Enable `logging` at `INFO` level or below on the `sasci360soldata.base.CI360DataBase` logger to see connection and request activity.

## Developer/Implementation Guide

### Configuration

`CI360DataConfig` is a dataclass holding connection and behavior settings:

```python
from sasci360soldata.base import CI360DataConfig

config = CI360DataConfig(
    algorithm="HS256",          # JWT signing algorithm
    api_base="/marketingData",
    encoding="utf-8",
    host="https://your-ci360-host.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
    timeout=30,                 # per-request timeout, seconds
    max_retries=3,
    retry_backoff=0.5,
    enable_compression=True,
)
```

`host`, `secret_key`, and `tenant_id` are required; the client raises `CI360DataValidationError` on construction if any are missing.

### Authentication

`CI360DataBase` generates a JWT on initialization (via [PyJWT](https://pyjwt.readthedocs.io/)) and attaches it to every request:

```python
headers = client.get_auth_headers()
# {"Authorization": "Bearer ...", "Content-Type": "application/json", ...}
```

### Data APIs

Every operation below has a synchronous method and an `_async` counterpart (e.g. `get_customers` / `get_customers_async`).

```python
# Customers
client.get_customers(limit=100, offset=0, filters=None)
client.get_customer(customer_id)
client.create_customer(customer_data)
client.update_customer(customer_id, customer_data)
client.delete_customer(customer_id)

# Segments
client.get_segments(limit=100, offset=0, filters=None)
client.get_segment(segment_id)
client.create_segment(segment_data)
client.update_segment(segment_id, segment_data)
client.delete_segment(segment_id)

# Import / export / schema
client.import_data(data, data_type="customers")
client.export_data(data_type="customers")
client.validate_data(data, data_type="customers")
client.get_schema(data_type="customers")
client.update_schema(data_type, schema)

# Import request jobs, file transfer, tables
client.get_import_request_jobs(start=0, limit=999, data_descriptor_id=None)
client.create_import_request_job(payload)
client.get_import_request_job(import_request_job_id)
client.create_file_transfer_location()
client.upload_to_signed_url(signed_url, file_path)
client.get_tables(start=0, limit=100, name=None, type=None)
client.get_table(table_id)
client.create_table(payload)
client.update_table(table_id, payload)
client.delete_table(table_id)
```

A full identity-bridge-style flow — upload a file, kick off an import request job, and poll it:

```python
transfer = client.create_file_transfer_location()
client.upload_to_signed_url(transfer["signedURL"], "/path/to/export.csv")

job = client.create_import_request_job({
    "dataDescriptorId": "my-table-id",
    "fileLocation": transfer["signedURL"],
})

job_detail = client.get_import_request_job(job["id"])
print(job_detail["statusInfo"]["importValidation"]["status"])
```

#### Async usage

```python
import asyncio
from sasci360soldata.base import CI360DataBase, CI360DataConfig

async def main():
    config = CI360DataConfig(
        host="https://your-ci360-host.sas.com",
        secret_key="your-secret-key",
        tenant_id="your-tenant-id",
    )
    async with CI360DataBase(config) as client:
        customer = await client.get_customer_async("customer-123")
        print(customer)

asyncio.run(main())
```

### Error Handling

```python
from sasci360soldata.base import (
    CI360DataBase,
    CI360DataAuthError,
    CI360DataConnectionError,
    CI360DataValidationError,
)

try:
    client = CI360DataBase(config)
    customers = client.get_customers()
except CI360DataValidationError as e:
    print(f"Invalid configuration: {e}")
except CI360DataAuthError as e:
    print(f"Authentication failed: {e}")
except CI360DataConnectionError as e:
    print(f"Connection error: {e}")
```

All of the above inherit from `CI360DataError`, the base exception for the module.

### Testing

See [tests/test_base.py](tests/test_base.py) for the full test suite (100% line coverage on `base.py`). It mocks at the `requests.Session` boundary — the actual point this client makes HTTP calls — rather than a higher-level method, so the connection and URL-construction logic are exercised, not just the call wiring:

```python
from unittest.mock import MagicMock, patch
from sasci360soldata.base import CI360DataBase, CI360DataConfig

@patch("sasci360soldata.base.requests.Session")
def test_get_customers(mock_session_class):
    mock_session = MagicMock()
    mock_session.request.return_value.status_code = 200
    mock_session.request.return_value.json.return_value = {"items": [], "total": 0}
    mock_session_class.return_value = mock_session

    config = CI360DataConfig(host="https://api.example.com", secret_key="test-secret", tenant_id="test-tenant")
    client = CI360DataBase(config)
    result = client.get_customers(limit=20)
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

For more information, see [Marketing Data API](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/rest-mkt-data.htm).
