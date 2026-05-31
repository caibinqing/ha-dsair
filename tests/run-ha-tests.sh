#!/usr/bin/env bash
#
# Run the DS-AIR Home Assistant integration test suite.
#
# Home Assistant core only runs on Linux/macOS (it imports POSIX-only modules
# such as `fcntl`), so on Windows run this inside WSL, not Git Bash / PowerShell.
#
# Requires `uv` (https://docs.astral.sh/uv/). The first run creates a cached
# virtualenv with Home Assistant + the test harness; later runs reuse it.
#
#   bash tests/run-ha-tests.sh             # run all tests
#   bash tests/run-ha-tests.sh -k flow -v  # extra args go to pytest
#
# Override the venv location with HA_TEST_VENV=/path/to/venv.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${HA_TEST_VENV:-$HOME/.cache/ha-dsair-testenv}"

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv not found. Install it with:" >&2
  echo "  curl -LsSf https://astral.sh/uv/install.sh | sh" >&2
  exit 1
fi

if [ ! -x "$VENV/bin/python" ]; then
  echo "== creating test venv at $VENV =="
  uv venv --python 3.13 "$VENV"
  uv pip install --python "$VENV" -r "$REPO/requirements_test.txt"
fi

echo "== running tests =="
cd "$REPO"
exec "$VENV/bin/python" -m pytest "$@"
