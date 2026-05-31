"""Integration test: the DS-AIR config flow creates a config entry end-to-end."""


async def test_user_flow_creates_entry(hass):
    """A user can complete the config flow and get a config entry."""
    result = await hass.config_entries.flow.async_init(
        "ds_air", context={"source": "user"}
    )
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    # Disabling sensors short-circuits straight to entry creation.
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "host": "192.168.1.50",
            "port": 8008,
            "gw": "DTA117C611",
            "scan_interval": 5,
            "sensors": False,
        },
    )
    assert result["type"] == "create_entry"
    assert result["title"] == "金制空气"
    assert result["data"]["host"] == "192.168.1.50"
    assert result["data"]["gw"] == "DTA117C611"
