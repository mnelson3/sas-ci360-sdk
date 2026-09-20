# Business Requirements Document — sas-ci360-sdk

| | |
| --- | --- |
| Document | BRD-CI360SDK-1.0 |
| Owner | Nelson Grey LLC |
| Scope | Layers 1–2 of the CI360 Connect toolkit: `api-core` and the 7 domain-client packages in this repository |
| Basis | Adapted from the CI360 Connect BRD/TRD/DD (v1.1, 2026-09-20), scoped to this repository |
| Related | [sas-ci360-solutions BRD](https://github.com/mnelson3/sas-ci360-solutions/blob/main/docs/BRD.md) (Layer 3) · [sas-ci360-plan-connector BRD](https://github.com/mnelson3/sas-ci360-plan-connector/blob/main/docs/BRD.md) (Layer 4) |

## 1. Executive summary

SAS ships Customer Intelligence 360 as a SaaS platform with a broad REST API surface, but minimal official developer tooling — a single data-download script and a handful of SAS-macro helpers. There is no official, general-purpose Python SDK covering the platform's REST API categories. This repository is that SDK: one independently pip-installable package per REST API category (Marketing Data, Marketing Gateway, Marketing Execution, Workflow, Plan, Digital Assets, SCIM), sharing one authentication/transport primitive (`api-core`).

It consolidates work that previously existed as 8 of a 17-repository family, across three overlapping generations built over several implementation cycles. The core concepts — REST API categories, JWT/Access Point authentication, the domain-client pattern — are validated against SAS's currently published documentation; the gap this repository closes is duplication, not currency.

## 2. Business context

### The gap in the CI360 ecosystem

SAS's own tooling is thin: `sassoftware/ci360-download-client-python` (a single Discover-data download script), a SAS-macro toolkit for the same purpose, and a mobile SDK. Every implementer who needs more than a data download — authentication handling, retry logic, per-API clients — currently writes it from scratch.

### What this repository does about it

One package per REST API category, sharing a common shape: a `…Config` dataclass, a `…Base` class with sync and async request paths, a typed exception hierarchy, mockable HTTP for real unit testing, and safe config fallbacks. `api-core` provides the one piece every package needs and none should duplicate: static-JWT generation and an HTTP session with retry.

### Why this repository, specifically

The 8 packages here were previously 8 separate repositories with duplicated CI/CD, duplicated dependency-declaration bugs (see TRD §2.8), and no single place an implementer could look to understand "what does this toolkit cover." Consolidating them into one repository with one CI workflow and one consistent package template removes that duplication without changing any package's public API.

## 3. Goals & objectives

| ID | Objective | Primary metric |
| --- | --- | --- |
| `CI360SDK-BG-1` | Give an implementer a working, authenticated API call in under 15 minutes from a fresh clone. | Time-to-first-call |
| `CI360SDK-BG-2` | Cover the CI360 REST API categories an implementer touches most. | 7/14 API categories covered |
| `CI360SDK-BG-3` | Reduce this repository to one canonical implementation per API category. | 0 duplicate client implementations |
| `CI360SDK-BG-4` | Make correctness verifiable without a live CI360 tenant wherever the API surface allows it. | % of tests running without live credentials |
| `CI360SDK-BG-5` | Where a live tenant genuinely is the only way to verify something (real auth, real connectivity), make that verifiable too, opt-in and never blocking normal CI. | UAT harness present and documented |

## 4. Stakeholders

- **Implementation engineer** (primary) — stands up a CI360 integration against a real client tenant on a deadline.
- **Integration architect** (primary) — evaluates whether to build on this toolkit or from scratch; cares about test coverage, license terms, and whether the design will still make sense in two years.
- **Individual consultant / hobbyist** (secondary) — personal projects, evaluation, learning the API surface.
- **Nelson Grey LLC** (commercial) — maintains the toolkit; monetizes production commercial use.

## 5. Scope

### In scope

| CI360 REST API | Package |
| --- | --- |
| Marketing Data API | `packages/sol-data` |
| Marketing Gateway API | `packages/marketing-gateway` |
| Marketing Execution API | `packages/sol-execute` |
| Workflow API | `packages/sol-workflow` |
| Plan API | `packages/sol-planning` (the Plan connector framework itself is `sas-ci360-plan-connector`, a separate repo) |
| Digital Assets API | `packages/sol-content-delivery` |
| SCIM API | `packages/sol-identity` |

### Out of scope for v1

Marketing Audience API, Marketing Design API, Marketing Administration API, Marketing Decisioning API, Decisioning Subject Contact API, Copy Item API, Container Image Management API — candidates for a v2 backlog.

### Explicitly out of scope

- Identity-bridge orchestration (Layer 3) — that's `sas-ci360-solutions`.
- The Plan connector framework / multi-cloud deployment (Layer 4) — that's `sas-ci360-plan-connector`.
- A hosted or managed version of any of this — these are libraries, run inside the implementer's own environment.
- UI-layer CI360 concepts (e.g. Real-time Journeys) — this repo operates at the REST API layer only.
- Non-Python runtimes.

## 6. Business requirements

| ID | Requirement | Priority |
| --- | --- | --- |
| `CI360SDK-BR-1` | Authenticate against a CI360 tenant using only values obtainable from CI360's own UI (Access Point host, tenant ID, client secret) — no undocumented setup steps. | P1 |
| `CI360SDK-BR-2` | Each package usable independently — installing one doesn't require installing another's dependencies. | P1 |
| `CI360SDK-BR-3` | No credential, tenant identifier, or client-specific data may appear in source, tests, or documentation. | P1 |
| `CI360SDK-BR-4` | Licensing terms visible before a prospective adopter writes any code against a package. | P1 |
| `CI360SDK-BR-5` | Exactly one implementation per API category in this repository; superseded implementations are archived elsewhere, not left live alongside their replacement. | P1 |

## 7. Success metrics

- **Time-to-first-call**: minutes from `git clone` to a successful authenticated API response, using only README instructions.
- **Test signal quality**: proportion of the test suite that exercises real logic with mocked HTTP at the correct boundary (`session.get`/`session.request`), versus tests that only prove "does not crash" or that mock the method under test.
- **CI health**: percentage of packages with a green pipeline on every push.
- **Consolidation debt**: count of API categories still implemented more than once in this repository (target: 0 — currently 0).

## 8. Assumptions & constraints

**Assumptions**
- The implementer already has a CI360 tenant and can create an Access Point.
- Integration tests that call a live gateway only ever run where real credentials are supplied — never in the default CI job.
- SAS continues to support HS256 static-JWT authentication as documented today.

**Constraints**
- `api-core` is a hard dependency for every domain-client package; it must stay small, stable, and independently versioned.
- Python 3.8–3.11 must remain supported until a documented deprecation cycle.
- No dependency may be added that isn't actually imported by the code that declares it.

## 9. Licensing

All packages in this repository are licensed under the **Nelson Grey LLC Community License 1.0**: free for personal, educational, non-commercial-research, and commercial-evaluation use; a paid commercial license is required for production commercial use; converts to Apache License 2.0 on **December 13, 2029**.
