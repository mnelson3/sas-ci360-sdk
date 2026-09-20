# Business Requirements Document — sasci360solidentity

| | |
| --- | --- |
| Document | BRD-SOLIDENTITY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-identity` (`sasci360solidentity`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`sol-identity` is the canonical client for CI360's SCIM API — user and group provisioning, authentication/token operations, and SCIM service-provider configuration. It's the SCIM-side counterpart to `sol-data`'s Marketing-Data-side role in the identity-bridge use case.

## 2. Business context

SCIM (System for Cross-domain Identity Management) is the standard CI360 exposes for identity-system synchronization — provisioning users/groups into or out of CI360 from an external HR/identity system. It supersedes `sas-ci360-api-scim` (archived).

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| `SOLIDENTITY-BG-1` | Cover user CRUD (including SCIM PATCH), group CRUD, auth/token operations, service-provider config, and bulk operations. | API surface parity with CI360's SCIM API |
| `SOLIDENTITY-BG-2` | Every operation verifiable without a live tenant — and without needing the private `api-core` package installed at all for unit tests. | 100% line coverage on `base.py` (achieved 2026-09-20) |
| `SOLIDENTITY-BG-3` | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT tests present (achieved 2026-09-20) |

## 4. Stakeholders

- **Implementation engineer** synchronizing an external identity/HR system with CI360.
- **`sas-ci360-solutions`** — a downstream consumer for the identity-bridge use case's identity-record side (the current identity-bridge implementation drives this indirectly rather than calling `sol-identity` directly; see that repo's own docs).

## 5. Scope

### In scope
User CRUD + SCIM PATCH; group CRUD; authenticate/validate-token/refresh-token; SCIM service-provider config get; bulk SCIM operations.

### Out of scope
See the parent repo's [BRD.md](../../../docs/BRD.md) §5.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| `SOLIDENTITY-BR-1` | Every request must land under `/scim`, not just at `host`'s root — including the SCIM `ServiceProviderConfig` health check. | P1 (real bug found and fixed, twice over — see TRD.md) |
| `SOLIDENTITY-BR-2` | Unit tests must not require the private `api-core` package to be installed. | P1 |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

SCIM version defaults to `2.0`; `1.1` is also accepted (validated against a fixed allow-list).

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
