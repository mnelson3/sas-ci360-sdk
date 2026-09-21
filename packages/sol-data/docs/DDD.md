# Detailed Design Document — sasci360soldata

| | |
| --- | --- |
| Document | DDD-SOLDATA-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/sol-data` (`sasci360soldata`) |

## Architecture

`sol-data` follows the standard Layer-2 domain-client pattern described in [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md): `CI360DataConfig(RestClientConfig)` dataclass, `CI360DataBase(RestClientBase)` class, sync/async pairs for every operation, a typed exception hierarchy (`CI360DataError`, `CI360DataAuthError`, `CI360DataConnectionError`, `CI360DataValidationError`) raised via `RestClientBase`'s shared code through 4 class attributes. `sol-data` has no extra `_validate_extra_config` or `_health_check_url` overrides — it takes the shared base's defaults as-is, unlike `sol-identity`.

`_generate_token()` — along with the rest of the connection/auth/request-dispatch boilerplate this used to define locally — now lives in `sasci360apicore.rest_client.RestClientBase` (added 2026-09-21, see the parent DDD.md's "Domain client pattern"). It's a plain top-level `from sasci360apicore.encryption import Encryption` there, no `try/except ImportError` guard: that guard existed because each package treated `api-core` as an optional dependency it might not have installed, which is moot now that the import lives inside `api-core` itself.

## The api_base URL bug

`_make_request_async` originally built its URL with:

```python
url = urljoin(self.config.host + self.config.api_base, endpoint.lstrip('/'))
```

`urljoin` treats a base URL with no trailing slash as a document to replace under RFC 3986, not a directory to extend — so this dropped `/marketingData` from every request. Fixed:

```python
url = f"{self.config.host.rstrip('/')}{self.config.api_base}/{endpoint.lstrip('/')}"
```

See [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §URL construction for the full explanation and why this was present across most of this repository's domain clients.

## `upload_to_signed_url`

Unlike every other method, this one does **not** go through `_make_request_async` / attach this client's own auth headers — the signed URL `create_file_transfer_location()` returns is already pre-authenticated by CI360 itself, and lives outside this client's `host`/`api_base`. It reads the local file and `PUT`s the raw bytes directly:

```python
response = self.session.put(signed_url, data=file_bytes, timeout=self.config.timeout)
```

Failures (missing file, network error) are wrapped as `CI360DataConnectionError`.

## Testing design

`tests/test_base.py` mocks at the `session.get`/`session.request` boundary for the connection-validation and `_make_request_async` tests specifically (rather than mocking `_make_request_async` itself, which every other test in the file does for the higher-level API methods — appropriate there, since those tests are about the method's own logic, not the request layer underneath it). `upload_to_signed_url`'s tests use `unittest.mock.mock_open` to avoid touching the real filesystem.

## CI/CD pipeline

Same as every package in this repository — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §CI/CD pipeline.
