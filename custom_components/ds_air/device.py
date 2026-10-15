"""Device registry helpers."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

# HA 2026.8 replaced the identifier-based `via_device` with the device registry id
# `via_device_id`; `via_device` stops working for custom integrations in 2027.8.
_HAS_VIA_DEVICE_ID = "via_device_id" in DeviceInfo.__annotations__


def via_gateway(hass: HomeAssistant, entry_id: str) -> DeviceInfo:
    """Return the DeviceInfo fields linking a device to the entry's gateway."""
    identifier = (DOMAIN, entry_id)
    if not _HAS_VIA_DEVICE_ID:
        return DeviceInfo(via_device=identifier)
    return DeviceInfo(
        via_device_id=dr.async_get_device_id_by_identifier(
            hass, identifier, config_entry_id=entry_id
        )
    )
