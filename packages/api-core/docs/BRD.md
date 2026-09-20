# Business Requirements Document — sasci360apicore

| | |
| --- | --- |
| Document | BRD-APICORE-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/api-core` (`sasci360apicore`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`api-core` is the one package every other package in this repository depends on. It has no CI360 REST API of its own — it provides the authentication, HTTP transport, and file-handling primitives that the seven domain clients build on, so none of them has to reimplement JWT generation or retry logic independently.

## 2. Business context

Before consolidation, this logic was duplicated across three generations of the codebase (and, separately, inside `automation-engine`, now archived). A bug fixed in one copy stayed a bug in the others. Centralizing it in one package, imported the same way by every domain client, means a fix here fixes every consumer at once.

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| `APICORE-BG-1` | Every domain client can generate a valid, CI360-accepted JWT from just a tenant ID and secret. | 0 auth failures traceable to this package's `Encryption` class |
| `APICORE-BG-2` | Every domain client gets retry-on-transient-failure without implementing it itself. | Identical `Retry`+`HTTPAdapter` config reused everywhere |
| `APICORE-BG-3` | Stay small and dependency-light — this package's own dependency list must actually match what it imports. | 0 `APICORE-NFR-8` violations (see TRD.md) |

## 4. Stakeholders

- **Every other package in this repository** — the direct consumer; this package's public API is a contract the other 7 packages depend on not breaking.
- **Implementation engineer** — never interacts with this package directly in normal use, but is affected by any bug in it across every client at once.

## 5. Scope

### In scope
- JWT generation (`Encryption`)
- HTTP transport with bounded retry (`Connection`)
- Outbound email (`Communication`)
- JSON response persistence (`Reporter`)
- Recurring job scheduling (`Scheduler`)
- File-processing helpers used by identity-bridge-style workflows (`Data`)

### Explicitly out of scope
- Anything CI360-domain-specific (endpoints, resource shapes) — that's every other package.
- A real SAS installation is required for `Data.create_sas_dataset()`'s live behavior; this package doesn't bundle or install SAS itself.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| `APICORE-BR-1` | `Encryption.generate_jwt()` must produce a token CI360 actually accepts, from just `secret_key` and `tenant_id`. | P1 |
| `APICORE-BR-2` | This package's own `install_requires` must not silently omit a dependency it needs — see the real bug fixed 2026-09-20 in TRD.md. | P1 |
| `APICORE-BR-3` | No credential-shaped value may appear in this package's source, tests, or fixtures. | P1 |

## 7. Success metrics

- Auth failures across all 7 consuming packages traceable to this package: 0.
- `pip install sasci360apicore` alone (no companion `requirements.txt`) installs a fully working set of dependencies.

## 8. Assumptions & constraints

- This package must stay small and stable — every domain client depends on it; a breaking change here breaks 7 packages at once.
- Python 3.6+ (the widest floor of any package in this repository, since it predates the others' 3.8 floor).

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
