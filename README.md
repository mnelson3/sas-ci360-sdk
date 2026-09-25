# SAS CI360 SDK

Python client libraries for [SAS Customer Intelligence 360](https://www.sas.com/en_us/software/customer-intelligence-360.html) — one independently pip-installable package per REST API category, plus the shared authentication and transport layer they all sit on.

> Licensed under the **Nelson Grey LLC Community License 1.0**: free for personal, educational, non-commercial-research, and commercial-evaluation use; a paid commercial license is required for production commercial use. Converts to Apache License 2.0 on **December 13, 2029**. See [LICENSE](LICENSE).

This repository is one of three that make up the CI360 Connect toolkit. The other two — [sas-ci360-solutions](https://github.com/mnelson3/sas-ci360-solutions) (identity-bridge orchestration) and [sas-ci360-plan-connector](https://github.com/mnelson3/sas-ci360-plan-connector) (multi-cloud Plan connector) — build on the packages here but have their own deployment lifecycles, so they stay in separate repositories.

For the full business/technical/design documentation behind this toolkit, see [`docs/`](docs/) in this repo. For a hands-on walkthrough of building something with it, see [`IMPLEMENTER_GUIDE.md`](IMPLEMENTER_GUIDE.md).

## Packages

| Package | CI360 REST API | Status |
| --- | --- | --- |
| [`packages/api-core`](packages/api-core) | Shared auth/transport primitives (no CI360 API of its own) | Canonical, Layer 1 |
| [`packages/sol-data`](packages/sol-data) | Marketing Data API | Canonical |
| [`packages/marketing-gateway`](packages/marketing-gateway) | Marketing Gateway API (Discover data-mart downloads) | Canonical |
| [`packages/sol-execute`](packages/sol-execute) | Marketing Execution API | Canonical |
| [`packages/sol-workflow`](packages/sol-workflow) | Workflow API | Canonical |
| [`packages/sol-planning`](packages/sol-planning) | Plan API | Canonical |
| [`packages/sol-content-delivery`](packages/sol-content-delivery) | Digital Assets API | Canonical |
| [`packages/sol-identity`](packages/sol-identity) | SCIM API | Canonical |

Each package has its own `README.md` (usage, API reference), `docs/` folder (BRD/TRD/DDD), `requirements.txt`, and test suite, and is installable on its own — an implementer who only needs Marketing Data does not have to install Workflow or SCIM dependencies. `api-core` is the one exception that's a hard dependency of every other package: it provides JWT authentication, HTTP transport with retry, and a handful of other shared primitives, none of it CI360-domain-specific.

## Quick start

```bash
git clone https://github.com/mnelson3/sas-ci360-sdk.git
cd sas-ci360-sdk/packages/sol-data
pip install -r requirements.txt
pip install -e .
```

```python
from sasci360soldata.base import CI360DataBase, CI360DataConfig

config = CI360DataConfig(
    host="https://extapigwservice-<env>.ci360.sas.com",
    secret_key="your-client-secret",
    tenant_id="your-tenant-id",
)
client = CI360DataBase(config)
customers = client.get_customers(limit=10)
```

`host`, `secret_key`, and `tenant_id` come from a CI360 Access Point (CI360 UI: General Settings → External Access → Access Points). Swap `sol-data`/`CI360Data*` for the package and class names in the table above for any other API.

## Testing

Every package has two tiers:

- **Unit tests** (`tests/test_base.py` or `tests/TestBase.py`) — fully mocked, no network access, safe anywhere. Run with `pytest tests/`. All seven packages are at 100% line coverage on their client's `base.py` as of 2026-09-20.
- **Live-tenant / UAT tests** (`tests/test_live_tenant.py`) — call a real CI360 tenant, skipped (not failed) unless `CI360_HOST`, `CI360_SECRET_KEY`, and `CI360_TENANT_ID` are set. See [`UAT.md`](UAT.md) for the full runbook.

## CI/CD

Every package runs the same four gates on push/PR to `main`, `staging`, `develop`: flake8 (hard errors always block), mypy, pytest with coverage, and a from-scratch dependency install. See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Repository history

This monorepo consolidates 8 of a 17-repository family (`api-core` plus the six `sol-*` clients plus `marketing-gateway`) that had accumulated three overlapping generations of the same idea over several implementation cycles. The other 9 repos in that family are archived (renamed with a `-archived` suffix, kept public, not deleted) rather than actively developed. See [`docs/DDD.md`](docs/DDD.md#consolidation) for the full rationale and [`docs/BRD.md`](docs/BRD.md) Appendix A for the complete repo-to-API map.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Scope a pull request to the package(s) it actually changes, and run that package's own test suite before submitting.

## License, security, support

- [`LICENSE`](LICENSE)
- [`SECURITY.md`](SECURITY.md) — how to report a vulnerability
- [`SUPPORT.md`](SUPPORT.md) — how to get help
