# Security Policy

## Supported Versions

This repository holds the SAS CI360 SDK — a monorepo of independently-installable Python client libraries (`packages/api-core`, `packages/sol-*`, `packages/marketing-gateway`) for the SAS Customer Intelligence 360 REST API family. Only the code currently deployed on each environment branch is supported — there is no long-term support for older commits.

| Branch | Environment | Status |
|---|---|---|
| `main` | Production | Supported |
| `staging` | Staging | Supported |
| `develop` | Development | Supported |

## Reporting a Vulnerability

This repository doesn't have a public issue tracker, so please don't report security concerns that way. Use one of:

- GitHub's [private vulnerability reporting](https://github.com/mnelson3/sas-ci360-sdk/security/advisories/new) (enabled on this repo), or
- Email **support@nelsongrey.com**

Either way, include:

- Which package(s) under `packages/` are affected
- A description of the vulnerability and its potential impact
- Steps to reproduce, or a proof of concept if available
- Any relevant logs, request/response samples, or affected endpoints

You should get an acknowledgement within a few business days.

## Automated Dependency Scanning

Dependabot alerts and security updates, native GitHub secret scanning (with push protection), and code scanning (CodeQL) are all enabled on this repository. Avoid committing credentials or secrets regardless — CI360 access point credentials (`host`, `secret_key`, `tenant_id`) are supplied by the caller at runtime via configuration, never committed to source.
