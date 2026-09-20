# Detailed Design Document — sasci360apicore

| | |
| --- | --- |
| Document | DDD-APICORE-1.0 |
| Owner | Nelson Grey LLC |
| Package | `packages/api-core` (`sasci360apicore`) |

## Architecture overview

`api-core` is Layer 1 of the CI360 Connect toolkit — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) for the full 4-layer picture. It sits below every domain client and is the only package in this repository with no CI360 REST API surface of its own.

## Module design

```
src/sasci360apicore/
├── encryption/    Encryption — JWT generation
├── connection/    Connection — HTTP with retry
├── communication/ Communication — SMTP email
├── reporter/      Reporter — JSON response persistence
├── scheduler/     Scheduler — recurring job execution
├── listener/      Listener — filesystem watching
├── logger/        Logger — structured logging setup
└── data/          Data — CSV/SAS-dataset file processing
```

Each module is independent — a consumer imports only what it needs (`from sasci360apicore.encryption import Encryption`), not the whole package.

## `Data.create_csv` — the header-duplication fix

The original implementation:

```python
for line in in_f:
    if is_header:
        out_f.write(line + "\n")
        rows = 1
    try:
        line = line.replace("|", "-").replace(in_delimiter, out_delimiter)
        out_f.write(line)
        rows += 1
    except IOError as e:
        ...
```

`is_header` was a per-call flag, not a per-line one — it stayed `True` for every line in the file, and the header branch never skipped the rest of the loop body. So with `is_header=True`, every single line got written twice: once verbatim (plus a stray extra blank line from the added `"\n"`) via the header branch, then again via the unconditional transform-and-write below.

Fixed:

```python
for line in in_f:
    if is_header:
        out_f.write(line.replace("|", "-").replace(in_delimiter, out_delimiter))
        rows = 1
        is_header = False
        continue
    try:
        line = line.replace("|", "-").replace(in_delimiter, out_delimiter)
        out_f.write(line)
        rows += 1
    except IOError as e:
        error = error + 1
        error_msg = error_msg + "\nerror in row: " + str(rows) + " - " + str(e)
if error:
    self.logger.warning("{0} row(s) failed to write: {1}".format(error, error_msg))
```

The header line now gets the same delimiter conversion as every other row (so the output file is internally consistent), is written exactly once, and the flag is cleared so subsequent lines take the normal path. The `error`/`error_msg` accumulator — previously built and then never used anywhere — is now logged once the file is done, so per-row write failures are visible instead of silently discarded.

## `setup.cfg` — the malformed install_requires fix

Before:

```ini
[install_requires]
package = pandas~=1.4.2
	PyJWT~=2.3.0
	...

[options]
package_dir = = src
packages = find:
python_requires = >=3.6
```

`[install_requires]` is not a section setuptools recognizes for this purpose — dependencies belong under `[options]` as an `install_requires =` key. The malformed section was silently ignored, so `pip install sasci360apicore` on its own installed zero dependencies. Every consuming package's `requirements.txt` masked this by redundantly re-declaring the same dependencies directly.

After:

```ini
[options]
package_dir = = src
packages = find:
python_requires = >=3.6
install_requires =
	pandas>=2.0.0
	PyJWT>=2.3.0
	requests>=2.27.1
	saspy>=4.2.0
	schedule>=1.1.0
	DateTime>=4.3
	urllib3>=2.0.0
```

Note the version pins also changed, not just the section: the original pins (`pandas~=1.4.2` etc.) were stale — 2022-era versions that fail to build at all on modern pip/setuptools (no bundled `pkg_resources`) — and conflicted with the newer pins in `requirements.txt` once actually wired up. The pins now match `requirements.txt` exactly.

## Testing design

`tests/TestData.py` is the reference example for testing code that depends on a real SAS installation without needing one: `saspy.SASsession`, `pandas.read_csv`, and `os.listdir` are all patched via `unittest.mock.patch`, so `create_sas_dataset` is fully exercised, including its `saspy.SASConfigNotFoundError` handling, with no SAS binary anywhere in the test environment. `create_csv`'s IOError-handling branch is tested by wrapping the real `open()` to return a handle whose `.write` is replaced with a `MagicMock(side_effect=IOError(...))` for the output file specifically — real file I/O for everything except the one failure being tested.

## CI/CD pipeline

Same as every other package — see [sas-ci360-sdk/docs/DDD.md](../../../docs/DDD.md) §CI/CD pipeline.
