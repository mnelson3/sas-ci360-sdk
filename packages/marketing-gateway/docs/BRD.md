# Business Requirements Document — sasci360apimarketinggateway

| | |
| --- | --- |
| Document | BRD-MARKETINGGATEWAY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/marketing-gateway` (`sasci360apimarketinggateway`) |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20) and [sas-ci360-sdk/docs](../../../docs) |

## 1. Executive summary

`marketing-gateway` is the canonical client for CI360's Marketing Gateway API — most notably the Discover service, which downloads data-mart extracts (Detail, DBT Report, Snapshot/Identity), plus event injection and configuration/agent management. It's the one package in this repository from an older client generation (predates the `sol-*` `Config`-dataclass pattern) with no newer replacement yet — see §5.

## 2. Business context

Discover is CI360's cloud data-mart download capability — the mechanism the identity-bridge use case (`sas-ci360-solutions`) uses to move CI360 identity data back out to an external system. It's the one CI360 REST API in this family with no `sol-*` equivalent, so this older-generation client remains canonical by default rather than by comparison.

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| `MARKETINGGATEWAY-BG-1` | Download Discover data-mart extracts with delta and time-range filtering. | API surface parity with CI360's Marketing Gateway API |
| `MARKETINGGATEWAY-BG-2` | `pip install` this package alone must actually pull in everything it needs. | 0 `MARKETINGGATEWAY-NFR-8` violations (1 was found and fixed — see TRD.md) |
| `MARKETINGGATEWAY-BG-3` | Every operation additionally verifiable against a real tenant, opt-in. | Live-tenant UAT test present (achieved 2026-09-20) |

## 4. Stakeholders

- **`sas-ci360-solutions`** — the primary real-world consumer of Discover downloads for the identity-bridge cycle.
- **Implementation engineer** doing Discover-based data-mart extraction independent of the identity-bridge use case.

## 5. Scope

### In scope
Root resource discovery (`get_root`); Discover data-mart downloads (Detail, DBT Report, Snapshot/Identity); event injection; configuration and agent management.

### Out of scope
A `sol-*`-generation rewrite of this package is not in scope for this iteration — it's functionally complete and covered, just structured differently (constructor-argument config rather than a `Config` dataclass, `unittest.TestCase`-style tests) from its 6 siblings. See the parent repo's [BRD.md](../../../docs/BRD.md) §5 for the full family scope.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| `MARKETINGGATEWAY-BR-1` | This package's declared dependencies must actually cover everything its code imports. | P1 (real bug found and fixed, see TRD.md) |
| `MARKETINGGATEWAY-BR-2` | `host` for this package's constructor is a bare hostname (this client builds its own `https://` prefix) — different from the `sol-*` packages' config, which needs the scheme included. | P2 (a real convention gap, documented; see [sas-ci360-sdk/IMPLEMENTER_GUIDE.md](../../../IMPLEMENTER_GUIDE.md) §3) |

## 7. Success metrics

Same as the parent repository — see [sas-ci360-sdk/docs/BRD.md](../../../docs/BRD.md) §7.

## 8. Assumptions & constraints

Assumes the caller passes `api="/marketingGateway"` (or the correct API path for whichever sub-resource) explicitly — this package's constructor takes it as a parameter rather than defaulting it per class, unlike the `sol-*` packages' `api_base` config field.

## 9. Licensing

Nelson Grey LLC Community License 1.0 — see [sas-ci360-sdk LICENSE](../../../LICENSE).
