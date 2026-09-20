# Business Requirements Document — sasci360solworkflow

| | |
| --- | --- |
| Document | BRD-SOLWORKFLOW-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-workflow` (`sasci360solworkflow`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`sol-workflow` is the canonical client for CI360's Workflow API — workflow definitions, process execution, triggers, and workflow templates.

## 2. Business context

CI360 Workflow drives process automation (e.g. multi-step customer journeys triggered by events). It supersedes `sas-ci360-api-workflow` (archived).

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| BG-1 | Cover workflow CRUD, process start/status/cancel, trigger CRUD, and templates. | API surface parity with CI360's Workflow API |
| BG-2 | Every operation verifiable without a live tenant. | 100% line coverage on `base.py` (achieved 2026-09-20) |
| BG-3 | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT tests present (achieved 2026-09-20) |
| BG-4 | Generate a JWT CI360 actually accepts. | 0 auth rejections traceable to this package |

## 4. Stakeholders

- **Implementation engineer** building or driving workflow-based process automation.

## 5. Scope

### In scope
Workflow CRUD; process start/status/cancel/listing; trigger CRUD; workflow template listing and workflow-from-template creation.

### Out of scope
See the parent repo's [BRD.md](../../../docs/BRD.md) §5.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| BR-1 | JWTs must use `api-core`'s canonical `Encryption` class, not a package-local reimplementation. | P1 (real bug found and fixed — see TRD.md) |
| BR-2 | Every request must land under `/marketingWorkflow`, not just at `host`'s root. | P1 (real bug found and fixed, see TRD.md) |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

Process execution on CI360's side is asynchronous — `get_process_status` polls, it doesn't block waiting for completion.

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
