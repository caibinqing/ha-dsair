"""Tests for migrating legacy unique IDs to gateway-scoped unique IDs.

Releases up to and including 2.0.0 give every device the unique ID
``daikin_{room_id}_{unit_id}``. That collides when two gateways expose the
same room/unit, which is the multi-gateway bug being fixed: the unique ID is
now scoped by config entry as ``daikin_{entry_id}_{room_id}_{unit_id}``.

For existing installs to keep their history, automations and customisations,
an ``async_migrate_entry`` must rewrite the entity/device registry (and the
``options.link`` sensor bindings) on upgrade.

``test_legacy_unique_id_mapping_spec`` is the executable spec for that mapping
and passes today. ``test_async_migrate_entry_end_to_end`` is the real
end-to-end test, skipped until the migration is restored in ``__init__.py``
(removed in caibinqing#3 commit "Remove legacy migrations").
"""

import pytest
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry


def _expected_migrated_unique_id(legacy: str, gateway_id: str) -> str | None:
    """Reference mapping the real ``async_migrate_entry`` must implement."""
    parts = legacy.split("_")
    if (
        len(parts) == 3
        and parts[0] == "daikin"
        and parts[1].isdigit()
        and parts[2].isdigit()
    ):
        return f"daikin_{gateway_id}_{parts[1]}_{parts[2]}"
    return None


async def test_legacy_unique_id_mapping_spec(hass):
    """A legacy entity's unique_id can be migrated while keeping its entity_id."""
    entry = MockConfigEntry(
        domain="ds_air",
        entry_id="abc123",
        data={"host": "x", "port": 8008, "gw": "DTA117C611", "scan_interval": 5},
    )
    entry.add_to_hass(hass)
    reg = er.async_get(hass)

    # Entity as written by the currently-released code.
    legacy = reg.async_get_or_create(
        "climate", "ds_air", "daikin_1_0", config_entry=entry
    )
    assert legacy.unique_id == "daikin_1_0"

    new_uid = _expected_migrated_unique_id("daikin_1_0", entry.entry_id)
    reg.async_update_entity(legacy.entity_id, new_unique_id=new_uid)

    migrated = reg.async_get(legacy.entity_id)
    # Same entity_id -> history and automations are preserved.
    assert migrated.entity_id == legacy.entity_id
    # New gateway-scoped unique_id -> no cross-gateway collisions.
    assert migrated.unique_id == "daikin_abc123_1_0"


def test_mapping_ignores_already_scoped_and_non_daikin_ids():
    """The mapping only rewrites legacy 3-part daikin IDs."""
    # Already gateway-scoped -> left alone (4 parts).
    assert _expected_migrated_unique_id("daikin_abc123_1_0", "xyz") is None
    # Unrelated unique IDs -> left alone.
    assert _expected_migrated_unique_id("something_else", "xyz") is None


@pytest.mark.skip(reason="enable once async_migrate_entry is restored (caibinqing#3)")
async def test_async_migrate_entry_end_to_end(hass):
    """Setting up a legacy entry should migrate its entities on upgrade.

    Intended shape once the migration lands:
        1. Add a MockConfigEntry at version=1, minor_version=1 and seed a
           legacy entity with unique_id "daikin_1_0".
        2. await hass.config_entries.async_setup(entry.entry_id)
        3. Assert the entity unique_id became "daikin_{entry_id}_1_0",
           the same entity_id was kept, and entry.minor_version was bumped.
    """
