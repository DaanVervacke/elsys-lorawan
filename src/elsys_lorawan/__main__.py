"""Discover ELSYS devices and print their readings."""

from lorawan_connection.cli_helper import run

from . import ElsysDeviceCollection


def main() -> None:
    """Run the ELSYS command-line interface."""
    run(ElsysDeviceCollection.DEVICES)


if __name__ == "__main__":
    main()
