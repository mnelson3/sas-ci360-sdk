# SAS Customer Intelligence 360

## SAS 360 API MARKETING GATEWAY LIBRARY

> **Status: canonical.** This is the actively maintained client for the Marketing Gateway API (Discover data downloads). No newer `sol-*` equivalent exists yet — this package predates the `Config`-dataclass generation the other packages use, and has its own shape (see below).

This is an independent, third-party client library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

The Marketing Gateway API downloads Discover data-mart extracts (base, detail, identity, reprocessed tables), injects external events, and reads on-premises agent/config info. This package provides five classes — `Root`, `DataDownload`, `Events`, `Agents`, `Configuration` — each constructed independently from the same six connection values, rather than sharing one `Config` dataclass.

For the full upstream API reference, see SAS's [Marketing Gateway API docs](https://support.sas.com/documentation/onlinedoc/ci/ci360-apis/marketingGateway/v2/redoc.html).

### Table of Contents

 - [Prerequisites](#prerequisites)
 - [Installation](#installation)
 - [Getting Started](#getting-started)
 - [API Marketing Gateway Code](#api-marketing-gateway-code)
 - [Troubleshooting](#troubleshooting)
 - [Contributing](#contributing)
 - [License](#license)
 - [Additional Resources](#additional-resources)

### Prerequisites

- Python 3.8+
- A Customer Intelligence 360 tenant with administrative rights
- `sasci360apicore` — this package's own dependency on the shared auth/transport library, pulled automatically from this same monorepo (see Installation)

**This package's `host` is a bare hostname** (e.g. `extapigwservice-prod.ci360.sas.com`), not a full URL — every class builds the `https://` prefix itself. This differs from the `sol-*` packages, which need `host` to already include `https://`.

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/marketing-gateway
pip install -r requirements.txt
pip install -e .
```

Installing this package alone does not pull in any other package's dependencies (Workflow, SCIM, etc.) beyond `sasci360apicore`.

### Getting Started

```python
from sasci360apimarketinggateway.root import Root

client = Root(
    algorithm="HS256",
    api="/marketingGateway",
    encoding="utf-8",
    host="extapigwservice-prod.ci360.sas.com",   # bare hostname, no https://
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

response = client.get_root()
print(response.json())
```

Every class in this package (`Root`, `DataDownload`, `Events`, `Agents`, `Configuration`) takes the same six positional arguments and returns a `requests.Response` from each method — call `.json()`, `.status_code`, etc. yourself, rather than getting a pre-parsed dict back.

### API Marketing Gateway Code

```python
from sasci360apimarketinggateway.data_download import DataDownload
from sasci360apimarketinggateway.events import Events
from sasci360apimarketinggateway.agents import Agents
from sasci360apimarketinggateway.configuration import Configuration

conn = dict(
    algorithm="HS256",
    api="/marketingGateway",
    encoding="utf-8",
    host="extapigwservice-prod.ci360.sas.com",
    secret_key="your-secret-key",
    tenant_id="your-tenant-id",
)

# Discover data-mart downloads (updated roughly every 4 hours; only completed sessions are available)
downloader = DataDownload(**conn)
downloader.get_base_tables()
downloader.get_detail_tables()
downloader.get_identity_tables()
downloader.get_reprocessed_tables()

# External events — the event name must already be defined in CI360 as an external event
events = Events(**conn)
events.create_external_event(payload={"eventName": "purchase", "eventData": {}})
events.create_bulk_events(payload={"events": []})

# On-premises agent downloads (no authentication required for the underlying endpoint)
agents = Agents(**conn)
agents.get_general_agent()      # includes the SDK
agents.get_diagnostics_agent()
agents.get_direct_agent()
agents.get_optimize_agent()

# API configuration
configuration = Configuration(**conn)
configuration.get_configuration()
```

### Troubleshooting

- Every method returns a raw `requests.Response`; check `.status_code` and call `.json()` yourself — these classes don't raise a typed exception hierarchy the way the newer `sol-*` packages do.
- Double-check `host` is a **bare hostname**, not a full URL — passing `https://...` here produces a malformed request URL.
- `Agents.get_general_agent()` (and the other agent endpoints) return a direct file download, not JSON — don't call `.json()` on that response.
- `Events.create_external_event`/`create_bulk_events` require the event name(s) to already exist in CI360 as defined external events; see [Working with External Events](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintwlma/n05dhxe32dd3own1e2iw0z7lkfw2.htm) in the SAS docs.
- This package depends on `sasci360apicore`'s `connection` and `encryption` modules; if you're seeing import errors, confirm `requirements.txt` installed successfully (it pulls `sasci360apicore` from this monorepo automatically).

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

For more information, see [REST APIs](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/ch-rest-apis.htm) and the [Marketing Gateway API reference](https://support.sas.com/documentation/onlinedoc/ci/ci360-apis/marketingGateway/v2/redoc.html).
