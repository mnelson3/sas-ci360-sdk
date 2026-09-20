# SAS Customer Intelligence 360

## SAS 360 API CORE LIBRARY

> **Status: canonical.** This is the shared authentication/transport library every other client in the family depends on. It has no CI360 API of its own — see the [root README](../../README.md) for the package that covers the API you actually need.

This is an independent, third-party library maintained by Nelson Grey LLC. It is not affiliated with or endorsed by SAS Institute.

### Overview

Eight small, independent modules — `Communication`, `Connection`, `Data`, `Encryption`, `Listener`, `Logger`, `Reporter`, `Scheduler` — providing JWT generation, retrying HTTP, email, CSV/SAS-dataset handling, file watching, logging, JSON-report persistence, and job scheduling. Every `sol-*` and `marketing-gateway` client in this monorepo is built on `Connection` and `Encryption`; the rest are optional utilities you can use directly in your own integration code.

### Table of Contents

 - [Prerequisites](#prerequisites)
 - [Installation](#installation)
 - [Getting Started](#getting-started)
 - [API Core Code](#api-core-code)
 - [Troubleshooting](#troubleshooting)
 - [Contributing](#contributing)
 - [License](#license)
 - [Additional Resources](#additional-resources)

### Prerequisites

- Python 3.8+

### Installation

This package lives in the `sas-ci360-sdk` monorepo:

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/api-core
pip install -r requirements.txt
pip install -e .
```

You normally don't install this package by itself — every `sol-*` package and `marketing-gateway` pulls it in automatically as a dependency. Install it directly only if you're using one of its modules (e.g. `Communication`, `Reporter`) standalone in your own code.

### Getting Started

The two modules every other package in this monorepo depends on:

```python
from sasci360apicore.encryption import Encryption
from sasci360apicore.connection import Connection

encryption = Encryption(algorithm="HS256", encoding="utf-8")
token = encryption.generate_jwt(secret_key="your-secret-key", tenant_id="your-tenant-id")

connection = Connection()
response = connection.connect(
    action="GET",
    headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    url="https://your-ci360-host.sas.com/marketingData/customers",
)
```

`Connection.connect()` retries up to 3 times (with a 3-second pause between attempts) on a non-2xx response, and returns the parsed JSON body, the raw bytes if the body isn't JSON, or the status code for an empty-body response (e.g. a signed-URL upload).

### API Core Code

```python
from sasci360apicore.communication import Communication
from sasci360apicore.data import Data
from sasci360apicore.listener import Listener
from sasci360apicore.logger import Logger
from sasci360apicore.reporter import Reporter
from sasci360apicore.scheduler import Scheduler

# Communication - send email
comm = Communication(
    email_server="smtp.example.com",
    email_server_login="user@example.com",
    email_server_password="your-password",
    email_server_port=587,
)
comm.send_email(
    email_msg_from="user@example.com",
    email_msg_to="recipient@example.com",
    email_msg_subject="CI360 job status",
    email_msg_body="The job completed successfully.",
)

# Data - convert a delimited file to CSV
data = Data()
data.create_csv(
    in_file="/path/to/input.txt",
    out_file="/path/to/output.csv",
    in_delimiter="\t",
    out_delimiter=",",
    is_header=True,
)

# Reporter - persist a JSON audit record
reporter = Reporter(root="/var/reports")
reporter.save(folder="/identity-bridge/", name="2026-09-20-status", data={"status": "success"})

# Listener - watch a folder for a file and move it out when it appears (blocks forever; run in its own thread/process)
listener = Listener(
    source_file="chain.dat",
    source_path="/watched/incoming",
    destination_file="chain.dat",
    destination_path="/watched/processed",
    sleep=30,
)
# listener.run()

# Scheduler - run a callable on a weekly schedule (blocks forever; run in its own thread/process)
scheduler = Scheduler(object=my_job_function, minute="00", hour="02", day="monday", sleep=60)
# scheduler.run()

# Logger - attach a file handler to the module's logger
logger = Logger().logging(log_file="/var/log/ci360-integration.log")
logger.info("Job started")
```

`Data.create_sas_dataset()` and `Data.get_schema()` additionally require a working local SAS installation reachable via [`saspy`](https://sassoftware.github.io/saspy/) — they're not usable without one.

### Troubleshooting

- These modules use `**kwargs` constructors with no defaults for required keys — a missing keyword raises `KeyError` inside the method, which most methods catch and log rather than re-raise; check the logger output (module name `sasci360apicore.<module>`) if a call silently returns `None`.
- `Connection.connect()` has no typed exception hierarchy — a persistent failure after 3 retries surfaces as whatever `requests` raised, or a non-2xx response passed through as-is.
- `Listener.run()` and `Scheduler.run()` both block forever in a loop — run them in their own thread, process, or service, not inline in a request-handling path.
- `Data.create_sas_dataset()` requires a real, licensed SAS installation via `saspy`; it will fail in any environment without one.

### Testing

Each module has its own test file under `tests/` (`TestCommunication.py`, `TestConnection.py`, `TestData.py`, `TestEncryption.py`, `TestListener.py`, `TestLogger.py`, `TestReporter.py`, `TestScheduler.py`), fully mocked — no network access or real SMTP/SAS session required:

```bash
pytest tests/
```

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

For more information, see [REST APIs](https://go.documentation.sas.com/doc/en/cintcdc/production.a/cintapis/ch-rest-apis.htm).
