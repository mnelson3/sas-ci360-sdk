# Detailed Design Document — sasci360solcontentdelivery

| | |
| --- | --- |
| Document | DDD-SOLCONTENTDELIVERY-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-content-delivery` (`sasci360solcontentdelivery`) |

## Architecture

Standard Layer-2 domain-client pattern — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md). `CI360ContentDeliveryBase` subclasses `sasci360apicore.rest_client.RestClientBase` (added 2026-09-21), which owns connection/auth/request-dispatch; this package defines only its `Config` extras (`max_file_size_mb`, `supported_formats`), its exception hierarchy — `CI360ContentDeliveryError`, `CI360ContentDeliveryAuthError`, `CI360ContentDeliveryConnectionError`, `CI360ContentDeliveryValidationError` (unchanged names, raised via the shared code through 4 class attributes) — and its domain methods.

## Why this package's gap mattered most

Every existing test in `tests/test_base.py` mocked `_make_request_async` itself — meaning the actual HTTP/connection/retry/error-handling logic underneath it, the most safety-critical code in the class, had zero direct coverage. This package is where testing one level deeper first surfaced the `urljoin` defect (see below) that turned out to be present across most of this repository's `sol-*` packages — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction for the full cross-package picture.

## The api_base URL bug — two mechanisms in one package

**`_make_request_async`**: `urljoin(self.config.host + self.config.api_base, endpoint.lstrip('/'))` — relative reference against a no-trailing-slash base, dropping `/digital-assets`. Fixed:

```python
url = f"{self.config.host.rstrip('/')}{self.config.api_base}/{endpoint.lstrip('/')}"
```

**`upload_asset_async`**: `urljoin(self.config.host + self.config.api_base, "/assets/upload")` — here the second argument is itself absolute, so `urljoin` replaces the whole path regardless of trailing slash, dropping `api_base` a different way than the first case. Fixed:

```python
url = f"{self.config.host.rstrip('/')}{self.config.api_base}/assets/upload"
```

## The missing-dependency bugs

`setup.cfg`'s `install_requires` had every one of this package's other dependencies but not `sasci360apicore` itself — meaning `pip install sasci360solcontentdelivery` alone (satisfied only by that file, not `requirements.txt`) would install a package that raises `CI360ContentDeliveryAuthError: Failed to generate authentication token: No module named 'sasci360apicore'` the moment `_generate_token()` runs. `requests-toolbelt`, imported inside `upload_asset_async` for its `MultipartEncoder`, was declared nowhere at all — same failure mode, different method. Both added to `requirements.txt` and `setup.cfg`.

## Testing design

`tests/test_base.py`'s new test classes (`TestCI360ContentDeliveryConnectionValidation`, `TestCI360ContentDeliveryMakeRequest`) are the pattern this repository's other packages copied for their own equivalent gap: mock `session.get`/`session.request` directly via `@patch('...base.requests.Session')`, not `_make_request_async`. `upload_asset`'s tests exercise the real multipart-encoding path with a mocked `session.post`.

## CI/CD pipeline

Same as every package in this repository.
