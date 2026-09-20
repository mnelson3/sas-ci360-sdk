# Technical Requirements Document — sasci360apicore

| | |
| --- | --- |
| Document | TRD-APICORE-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/api-core` (`sasci360apicore`) |

## 1. Functional requirements

| ID | Requirement | Class |
| --- | --- | --- |
| APICORE-FR-1 | Generate a static JWT: base64-encoded secret key, HS256, `{"clientID": tenant_id}` payload. | `Encryption.generate_jwt(secret_key, tenant_id)` |
| APICORE-FR-2 | Make an HTTP call with headers/data/params, returning a parsed response. | `Connection.connect(action, url, headers, data, params)` |
| APICORE-FR-3 | Send an outbound email over SMTP. | `Communication.send_email(...)` |
| APICORE-FR-4 | Persist a response payload as a timestamped JSON file, creating the target directory if missing. | `Reporter.save(folder, name, data)` |
| APICORE-FR-5 | Run a job on a recurring interval. | `Scheduler.chain_run()` / `Scheduler.change_run()` |
| APICORE-FR-6 | Convert a delimited text file to CSV, writing the header once (delimiter-converted) and each data row once. | `Data.create_csv(in_file, out_file, in_delimiter, out_delimiter, is_header)` |
| APICORE-FR-7 | Load CSV files from a directory into SAS datasets via a live SAS session. | `Data.create_sas_dataset(filename, gDirClean)` |
| APICORE-FR-8 | Build a delimiter-joined column header string from a JSON schema description for a named table. | `Data.get_schema(source, table_name, delimiter)` |

## 2. Non-functional requirements

| ID | Category | Requirement | Status (2026-09-20) |
| --- | --- | --- | --- |
| APICORE-NFR-1 | Correctness | `create_csv`'s header handling must write the header exactly once and not duplicate data rows. | **Real bug fixed**: the header flag was checked on every loop iteration, not just the first, so every row was written twice when `is_header=True`. Fixed to clear the flag and `continue` after the header line. |
| APICORE-NFR-2 | Observability | Per-row write failures during `create_csv` must be surfaced, not silently discarded. | **Real bug fixed**: failures were counted into a message that was built but never logged or returned. Now logged via `self.logger.warning`. |
| APICORE-NFR-3 | Packaging hygiene | `setup.cfg`'s `install_requires` must actually be read by setuptools. | **Real bug fixed**: the dependencies were declared under a malformed `[install_requires]` section instead of `[options] install_requires =`, silently ignored — a bare `pip install` of this package installed zero dependencies. Fixed. |
| APICORE-NFR-4 | Testability | Every method testable without a real SAS installation or real SMTP server. | Verified: `create_sas_dataset` mocks `saspy.SASsession`; `Communication` tests mock the SMTP layer. |

## 3. Data requirements

No persistent data model of its own. `Reporter.save()` writes arbitrary JSON payloads under a caller-specified root path; `Data.create_sas_dataset()` reads CSVs from a caller-specified directory.

## 4. Technology stack

`pandas`, `PyJWT`, `requests`, `saspy`, `schedule`, `DateTime`, `urllib3`. `saspy` is the one dependency the rest of this repository's packages don't need — it's specific to `Data.create_sas_dataset()`.

## 5. Dependency policy

This package's own `install_requires` (in `setup.cfg`) is what every consuming package's `requirements.txt` re-declares redundantly (see [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md) APICORE-NFR-8) to work around the fact that, until 2026-09-20, this section was silently ignored. It's fixed now, but the redundant re-declarations in `sol-*` packages' own `requirements.txt` files are left in place rather than removed — belt-and-suspenders against this class of bug recurring, and low-cost to keep.

## 6. Testing strategy

Unit tests (`tests/TestEncryption.py`, `TestConnection.py`, `TestCommunication.py`, `TestReporter.py`, `TestScheduler.py`, `TestListener.py`, `TestLogger.py`, `TestData.py`) mock `requests.get`/`requests.post` directly (this package predates the `sol-*` packages' `Session`-object pattern) and, for `Data`, mock `saspy.SASsession`/`pandas.read_csv`/`os.listdir` so no real SAS install or filesystem fixture beyond a `tempfile.TemporaryDirectory()` is needed. `TestData.py`'s `create_sas_dataset` tests are the reference example for mocking `saspy` — see [DDD.md](DDD.md) §Testing design.

`data/__init__.py` was the one module in this package with no tests at all until 2026-09-20 (16% line coverage); it's at 99% now (the one line left is the `if __name__ == "__main__":` guard).

## 7. CI/CD requirements

Same four-gate workflow as every other package in this repository — see [sas-ci360-sdk/docs/TRD.md](../../../docs/TRD.md) §10.
