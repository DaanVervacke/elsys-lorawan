"""ELSYS device models for ChirpStack and The Things Stack."""

from lorawan_connection import DeviceCollection

from .decoders import decode_elsys
from .device import ElsysDevice
from .models import (
    ELT2,
    EMS,
    ERS,
    ERSCO2,
    ERSVOC,
    ELTLite,
    ELTUltrasonic,
    EMSDesk,
    EMSDoor,
    EMSLite,
    ERSCO2Lite,
    ERSEye,
    ERSLite,
    ERSSound,
)
from .payload import DecodedPayload, Measurement


def decode_elsys_payload(data: bytes) -> dict[str, float | bool | int | str]:
    """Decode an ELSYS uplink into a plain dictionary."""
    result: dict[str, float | bool | int | str] = {}
    value: float | bool | int | str
    for item in ElsysDevice.decode(data).measurements:
        if item.value is not None:
            if isinstance(item.value, (float, bool, int, str)):
                value = item.value
                result[item.name] = value
    return result


class ElsysDeviceCollection(DeviceCollection[ElsysDevice]):
    """Discover ELSYS devices using official catalog identities."""

    DEVICES = (
        ERS,
        ERSLite,
        ERSCO2,
        ERSCO2Lite,
        ERSVOC,
        ERSSound,
        ERSEye,
        ELT2,
        ELTLite,
        ELTUltrasonic,
        EMS,
        EMSDoor,
        EMSLite,
        EMSDesk,
    )


__all__ = [
    "DecodedPayload",
    "ELT2",
    "ELTLite",
    "ELTUltrasonic",
    "EMS",
    "EMSDesk",
    "EMSDoor",
    "EMSLite",
    "ERS",
    "ERSCO2",
    "ERSCO2Lite",
    "ERSEye",
    "ERSLite",
    "ERSSound",
    "ERSVOC",
    "ElsysDevice",
    "ElsysDeviceCollection",
    "Measurement",
    "decode_elsys",
    "decode_elsys_payload",
]
