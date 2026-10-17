"""Run the installed command against a simulated backend."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from lorawan_connection import DeviceDescriptor
from lorawan_connection.mock import MockConnection

from elsys_lorawan import ERS
from elsys_lorawan.__main__ import main


# ELSYS devices carry The Things Stack catalog identities only: the
# ChirpStack device-profile catalog lists Elsys without a numeric
# vendor id, so there is no stable ChirpStack identity to match on.
@pytest.mark.parametrize("backend", ["tts"])
def test_list_devices(backend: str, capsys: pytest.CaptureFixture[str]) -> None:
    """The backend selection lists supported devices and closes the connection."""
    identifiers = ERS.identifiers.get(backend, ("elsys", "ers"))
    descriptor = DeviceDescriptor(
        network_id="network",
        dev_eui="0201010101010101",
        name="Living room",
        stack=backend,
        brand_id=identifiers[0],
        model_id=identifiers[1],
        application_id="application",
        profile_id="profile",
    )
    connection = MockConnection([descriptor], stack_type=backend)
    connection.inventory = AsyncMock(return_value=[descriptor])
    connection.close = AsyncMock()
    with (
        patch(
            "sys.argv",
            [
                "elsys-lorawan",
                "--backend",
                backend,
                "--server",
                "https://example.com",
                "--list",
                "--json",
            ],
        ),
        patch(
            "lorawan_connection.cli_helper.connect_from_args",
            return_value=connection,
        ) as connect,
    ):
        main()
    assert connect.call_args.args[0].backend == backend
    data = json.loads(capsys.readouterr().out)
    assert data["model"] == "ERS"
    assert data["name"] == "Living room"
    assert data["state"]["temperature"] is None
    connection.close.assert_awaited_once_with()
