"""Pytest fixtures for the DS-AIR integration tests.

These tests use the real Home Assistant test harness
(``pytest-homeassistant-custom-component``), which only runs on Linux/macOS:
HA core imports POSIX-only modules such as ``fcntl``. On Windows, run them
inside WSL. See ``tests/README.md``.

The harness ships its own ``custom_components`` package (a *regular* package,
with ``__init__.py``, inside its bundled ``testing_config``) which shadows this
repo's namespace ``custom_components``. We extend that package's ``__path__``
so Home Assistant also discovers ``ds_air`` from this repo -- otherwise setup
fails with "Cannot find integration ds_air".
"""

import pathlib

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

_REPO_CUSTOM_COMPONENTS = str(
    pathlib.Path(__file__).resolve().parent.parent / "custom_components"
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Make this repo's ``custom_components/ds_air`` discoverable, then enable it."""
    import custom_components

    if _REPO_CUSTOM_COMPONENTS not in list(custom_components.__path__):
        custom_components.__path__.append(_REPO_CUSTOM_COMPONENTS)
    yield
