# User acceptance testing (live-tenant integration tests)

Every package's unit test suite mocks CI360 entirely (see each README):
no network access, no credentials, safe to run anywhere including CI.
This document covers the other tier described in the design doc's
testing strategy (§2.9) - tests that call a *real* CI360 tenant to
verify the whole stack actually works end to end, not just that the
mocked request-construction logic looks right.

These tests are opt-in. They never run in CI (no repository secrets are
configured for them, deliberately), and locally they're skipped rather
than failed unless you explicitly provide credentials.

## Status (as of 2026-09-21)

This harness has been built and unit-tested (the `pytest.mark.skipif`
gating itself is verified), but **not yet executed against a real
tenant** - no CI360 Access Point credentials (training or production)
were available in this environment as of this writing. Until someone
with access to a licensed CI360 tenant runs this tier at least once,
"the SDK works against a real API" is a design intent backed by
extensive mocked-at-the-session-boundary unit tests, not a confirmed
fact. Treat that as the highest-priority open verification step before
depending on this SDK for anything live - see each package's own
mocked unit tests for what *has* been verified (request construction,
URL building, error mapping), and this section for what hasn't
(whether CI360 actually accepts and responds to those requests as
expected).

## What's covered

One `test_live_tenant.py` (or `TestLiveTenant.py` for the two packages
that follow the older unittest-style convention) per package that talks
to CI360 directly:

| Package | What it calls |
| --- | --- |
| `packages/sol-data` | `get_tables`, `get_customers` |
| `packages/sol-execute` | `get_batch_jobs`, `get_scheduled_jobs` |
| `packages/sol-workflow` | `get_workflows`, `get_workflow_templates` |
| `packages/sol-identity` | `get_users`, `get_service_provider_config` |
| `packages/sol-content-delivery` | `get_assets`, `get_content_templates` |
| `packages/sol-planning` | `get_campaigns`, `get_audiences` |
| `packages/marketing-gateway` | `get_root` |

Every call is a **read-only GET**. None of these tests create, update,
or delete anything in the tenant they run against - they exist to prove
authentication and connectivity work, not to exercise every endpoint.
Each package also gets a `validate_connection()` assertion where that
method exists, which is the most direct proof that a real JWT was
accepted by CI360.

This intentionally does not cover:

- **Mutating operations** (create/update/delete). Exercising those live
  needs a disposable tenant or careful cleanup, which is out of scope
  for this pass - a harness, not a full live-tenant regression suite.
- **`sas-ci360-solutions`** (the identity-bridge orchestration) and
  **`sas-ci360-plan-connector`** (the multi-cloud connector). Both
  compose the clients covered here plus additional systems (email,
  cloud secret stores, a partner API) that would need their own
  credentials and non-trivial setup to exercise live. Worth a follow-up
  pass, not attempted here.

## Running them

You need a real CI360 tenant and an Access Point (CI360 UI: General
Settings → External Access → Access Points) to obtain a host, tenant
ID, and client secret - the same three values every package's own
README already documents for normal use.

```bash
export CI360_HOST="extapigwservice-<env>.ci360.sas.com"   # bare hostname, no scheme
export CI360_SECRET_KEY="your-client-secret"
export CI360_TENANT_ID="your-tenant-id"
```

`CI360_HOST` is a bare hostname (the value CI360's Access Point screen
shows you directly). The `sol-*` packages' own config needs a full
`https://` URL; each `test_live_tenant.py` adds the scheme itself if
you didn't include one, so the same three values work unmodified across
every package.

Then, from any one package directory:

```bash
cd packages/sol-data
pip install -r requirements.txt && pip install -e .
pip install pytest
pytest tests/test_live_tenant.py -v
```

Repeat per package, or run all of them from the repo root:

```bash
for pkg in sol-data sol-execute sol-workflow sol-identity sol-content-delivery sol-planning; do
  (cd "packages/$pkg" && python -m pytest tests/test_live_tenant.py -v)
done
(cd packages/marketing-gateway && python -m pytest tests/TestLiveTenant.py -v)
```

With no credentials set, every one of these commands reports the tests
as **skipped** (not failed, not an error) - that's the safe default
this harness is built around, not a sign anything is broken.

## Using a non-production tenant

Point `CI360_HOST` and `CI360_TENANT_ID` at a training/test tenant
Access Point instead of production if you have one - nothing about
these tests requires production. Since every call is read-only, running
against production is not destructive, but a test/training tenant is
still the safer default if one is available to you.

## Wiring this into CI (not done yet)

If you want a scheduled or manually-triggered CI job to run this tier
against a real tenant, add `CI360_HOST`, `CI360_SECRET_KEY`, and
`CI360_TENANT_ID` as repository secrets and add a `workflow_dispatch`-
triggered job (separate from the push/PR `ci.yml` job, so a credential
or tenant outage never blocks a normal merge) that exports them and runs
the commands above. That wiring itself - the workflow YAML and the
actual GitHub secrets - hasn't been set up as part of this pass, since
it requires decisions (which tenant, who holds the credentials, how
often to run it) that belong to whoever operates this repository, not
to this document.
