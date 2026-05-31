# Tests

| File | Needs Home Assistant? | Runs on Windows? |
| --- | --- | --- |
| `test_config_flow.py`, `test_migration.py` | Yes (real `hass` fixture) | ❌ Linux/macOS/WSL only |
| `test_temperature_scaling.py` | No (stubs HA modules) | ✅ yes |
| `test.py`, `protocol-demo.txt` | manual protocol scratch, not collected | — |

CI runs the suite on every push and pull request
(`.github/workflows/test.yml`, Ubuntu).

## Running locally

```bash
pip install -r requirements_test.txt
pytest
```

Or use the helper script, which manages a cached
[`uv`](https://docs.astral.sh/uv/) venv for you:

```bash
bash tests/run-ha-tests.sh            # all tests
bash tests/run-ha-tests.sh -k migration -v   # extra args go to pytest
```

### On Windows

Home Assistant core imports POSIX-only modules (e.g. `fcntl` in
`homeassistant/runner.py`), so the `pytest-homeassistant-custom-component`
harness cannot run on native Windows — HA itself is only supported on Linux.
Run the suite inside **WSL** from the repo root:

```powershell
wsl bash -lc 'bash tests/run-ha-tests.sh'
```

## Harness note

`pytest-homeassistant-custom-component` ships its own `custom_components`
package (inside its `testing_config`) which shadows this repo's. `conftest.py`
extends that package's `__path__` so Home Assistant also discovers `ds_air`
from this repo; without it, setup fails with `Cannot find integration ds_air`.
