# Business Requirements Document — sasci360solplanning

| | |
| --- | --- |
| Document | BRD-SOLPLANNING-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-planning` (`sasci360solplanning`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`sol-planning` is the canonical client for CI360's Plan API — campaigns, audiences, and campaign analytics. It's the CI360-side counterpart to `sas-ci360-plan-connector`, which uses the Plan API's connector framework (a related but distinct mechanism) to sync offers with a third-party platform.

## 2. Business context

Plan is CI360's marketing-planning surface — campaigns and their target audiences, plus analytics on how they perform. It supersedes `sas-ci360-api-plan` (archived).

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| `SOLPLANNING-BG-1` | Cover campaign CRUD, audience CRUD, and campaign analytics. | API surface parity with CI360's Plan API |
| `SOLPLANNING-BG-2` | Every operation verifiable without a live tenant. | Coverage present since before 2026-09-20's testing pass |
| `SOLPLANNING-BG-3` | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT tests present (achieved 2026-09-20) |
| `SOLPLANNING-BG-4` | Generate a JWT CI360 actually accepts. | 0 auth rejections traceable to this package |

## 4. Stakeholders

- **Implementation engineer** building or managing campaigns and audiences programmatically.
- **`sas-ci360-plan-connector`** — a related but separate system; does not import this package directly (it talks to CI360's connector framework, a different mechanism from this client's direct Plan API calls).

## 5. Scope

### In scope
Campaign CRUD; audience CRUD, including size estimation; campaign analytics and optimization; campaign templates.

### Out of scope
The Plan connector framework itself (third-party offer sync) — that's `sas-ci360-plan-connector`, a separate repository. See the parent repo's [BRD.md](../../../docs/BRD.md) §5 for the full family scope.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| `SOLPLANNING-BR-1` | JWTs must use `api-core`'s canonical `Encryption` class, not a package-local reimplementation. | P1 (real bug found and fixed — see TRD.md) |
| `SOLPLANNING-BR-2` | Every request must land under `/marketingPlanning`, not just at `host`'s root. | P1 (real bug found and fixed — see TRD.md) |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

None beyond the parent repository's — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §8.

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
