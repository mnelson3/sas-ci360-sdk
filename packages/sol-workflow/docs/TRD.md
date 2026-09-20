# Technical Requirements Document — sasci360solworkflow

| | |
| --- | --- |
| Document | TRD-SOLWORKFLOW-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-workflow` (`sasci360solworkflow`) |

## 1. Functional requirements

| ID | Requirement | Method |
| --- | --- | --- |
| `SOLWORKFLOW-FR-1` | List/get/create/update/delete workflows (with filters on list). | `get_workflows`, `get_workflow`, `create_workflow`, `update_workflow`, `delete_workflow` (+ `_async`) |
| `SOLWORKFLOW-FR-2` | Start a process; get its status; cancel it; list processes (status filter). | `start_process`, `get_process_status`, `cancel_process`, `get_processes` (+ `_async`) |
| `SOLWORKFLOW-FR-3` | List/create/update/delete triggers (with filters on list). | `get_triggers`, `create_trigger`, `update_trigger`, `delete_trigger` (+ `_async`) |
| `SOLWORKFLOW-FR-4` | List workflow templates (category filter); create a workflow from a template. | `get_workflow_templates`, `create_workflow_from_template` (+ `_async`) |

`api_base` default: `/marketingWorkflow`.

## 2. Non-functional requirements

Inherits `SOLWORKFLOW-NFR-1` through `SOLWORKFLOW-NFR-8` from [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md). Status specific to this package as of 2026-09-20:

| ID | Status |
| --- | --- |
| `SOLWORKFLOW-NFR-1` (Auth correctness) | **Real bug found and fixed during the monorepo migration**: this package (and `sol-planning`) generated JWTs with the wrong payload shape and an unencoded signing key — CI360 would have rejected them outright, despite both passing their own mocked unit tests. Fixed by delegating to `api-core`'s canonical `Encryption` class, matching every other client. |
| `SOLWORKFLOW-NFR-4` (Testability, correct boundary) | **Fixed**: same `urljoin` api_base-dropping defect as `sol-data`, `sol-execute`, and `sol-identity`. Fixed to plain string formatting. |
| Coverage | 67% → 100% on `base.py` (60 tests). |
| Config validation | `max_concurrent_workflows <= 0` raises `CI360WorkflowValidationError`. |

## 3. Data requirements

`CI360WorkflowConfig`: the standard fields plus `max_concurrent_workflows` (default 50), `workflow_timeout` (default 7200).

## 4. Technology stack

Same as the parent repository.

## 5. Dependency policy

Same `SOLWORKFLOW-NFR-8` pattern as every `sol-*` package; this package's `requirements.txt`/`setup.cfg` were also missing `pandas`/`saspy`/`schedule`/`DateTime` (the transitive deps every sibling redundantly re-declares) until 2026-09-20 — see the parent TRD's `SOLWORKFLOW-NFR-8` note. Fixed.

## 6. Testing strategy

`tests/test_base.py` — 60 tests, 100% line coverage, including config validation error branches, both `_generate_token` failure modes, real context-manager success/failure paths (sync and async), and every previously-untested sync wrapper and filter-merge branch.

`tests/test_live_tenant.py` — calls `get_workflows`/`get_workflow_templates` and `validate_connection()` against a real tenant. See [sas-ci360-sdk/UAT.md](../../../UAT.md).

## 7. CI/CD requirements

Same four-gate workflow as every package in this repository.
