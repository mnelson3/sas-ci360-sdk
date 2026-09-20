# Business Requirements Document — sasci360solexecute

| | |
| --- | --- |
| Document | BRD-SOLEXECUTE-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-execute` (`sasci360solexecute`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`sol-execute` is the canonical client for CI360's Marketing Execution API — campaign execution, batch job submission/monitoring, job scheduling, and execution metrics.

## 2. Business context

Where `sol-data` moves records and `sol-workflow` drives process automation, `sol-execute` is specifically about *running* things: executing a campaign, submitting a batch job, and tracking their status. It supersedes `sas-ci360-api-marketing-execution` (archived).

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| `SOLEXECUTE-BG-1` | Cover campaign execution, batch jobs, scheduling, and metrics end to end (start, monitor, cancel). | API surface parity with CI360's Marketing Execution API |
| `SOLEXECUTE-BG-2` | Every operation verifiable without a live tenant. | 100% line coverage on `base.py` (achieved 2026-09-20) |
| `SOLEXECUTE-BG-3` | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT tests present (achieved 2026-09-20) |

## 4. Stakeholders

- **Implementation engineer** running or scheduling campaign executions and batch jobs.

## 5. Scope

### In scope
Campaign execution and status; execution cancellation; batch job submission, status, cancellation, and listing; job scheduling (create/list/update/delete); execution metrics.

### Out of scope
See the parent repo's [BRD.md](../../../docs/BRD.md) §5.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| `SOLEXECUTE-BR-1` | Every request must land under `/marketingExecution`, not just at `host`'s root. | P1 (real bug found and fixed, see TRD.md) |
| `SOLEXECUTE-BR-2` | `batch_size` config must be validated positive before use. | P2 |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

Batch and scheduled-job execution on CI360's side is asynchronous — this client's job-status methods poll, they don't block waiting for completion.

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
