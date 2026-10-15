"""Integration test: devices are linked to their gateway device."""

from unittest.mock import patch

from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.ds_air.const import DOMAIN
from custom_components.ds_air.ds_air_service import AirCon, Service, Ventilation


def _fake_init(self, host, port, scan_interval, config, timeout=None):
    aircon = AirCon(config)
    aircon.alias = "客厅"
    aircon.room_id, aircon.unit_id = 1, 0
    vent = Ventilation(config)
    vent.alias = "书房"
    vent.room_id, vent.unit_id = 2, 0
    vent.is_small_vam = True
    self._config = config
    self._aircons = [aircon]
    self._ventilations = [vent]


async def test_devices_link_to_gateway(hass, caplog):
    """Every device must hang off the entry's gateway device."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        title="金制空气",
        data={"host": "192.168.1.50", "port": 8008, "gw": "DTA117C611", "scan_interval": 5},
    )
    entry.add_to_hass(hass)

    with patch.object(Service, "init", _fake_init):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    device_registry = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    gateway = next(
        device for device in devices if (DOMAIN, entry.entry_id) in device.identifiers
    )
    assert gateway.via_device_id is None

    children = [device for device in devices if device.id != gateway.id]
    # aircon + ventilation
    assert len(children) == 2
    assert all(device.via_device_id == gateway.id for device in children)
    # HA 2026.8+ reports `via_device` as deprecated in favour of `via_device_id`.
    assert "deprecated `via_device`" not in caplog.text

    assert await hass.config_entries.async_unload(entry.entry_id)
