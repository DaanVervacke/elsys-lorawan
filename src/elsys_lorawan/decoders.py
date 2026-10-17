"""Decoder for the ELSYS unified TLV uplink payload.

Ported from ELSYS's public payload decoder (TheThingsNetwork
lorawan-devices vendor/elsys/elsys.js) and the official uplink
application note. Every ELSYS device shares one payload format:
each measurement is a 1-byte type followed by a fixed-length
value, optionally with a timestamp appended when measurement
timestamping is enabled (the upper 2 bits of the type byte give
the timestamp size: 0, 1, 2, or 4 bytes of seconds-ago).

Unknown type codes abort the parse (keeping already-decoded
measurements), matching the official decoder. Truncated values
raise ValueError.
"""

from collections.abc import Callable

from .payload import DecodedPayload, Measurement, Timestamp, Value

type Factory = Callable[[bytes, int], Value]

_TIMESTAMP_SIZES = (0, 1, 2, 4)


def _int8(data: bytes, offset: int) -> int:
    value = data[offset]
    return value - 256 if value & 0x80 else value


def _int16(data: bytes, offset: int) -> int:
    value = int.from_bytes(data[offset : offset + 2], "big")
    return value - 65536 if value & 0x8000 else value


def _int24(data: bytes, offset: int) -> int:
    value = int.from_bytes(data[offset : offset + 3], "big")
    return value - 16777216 if value & 0x800000 else value


def _int32(data: bytes, offset: int) -> int:
    value = int.from_bytes(data[offset : offset + 4], "big")
    return value - 4294967296 if value & 0x80000000 else value


def _uint16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 2], "big")


def _uint32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset : offset + 4], "big")


def _room_ir(data: bytes, offset: int) -> list[Value]:
    reference = data[offset]
    pixels: list[Value] = []
    for index in range(64):
        pixels.append(reference + _int8(data, offset + 1 + index) / 10)
    return pixels


# type code -> (value byte length, name, value factory)
_TYPES: dict[int, tuple[int, str, Factory | None]] = {
    0x01: (2, "temperature", lambda d, o: _int16(d, o) / 10),
    0x02: (1, "humidity", lambda d, o: d[o]),
    0x03: (3, "acceleration", None),
    0x04: (2, "light", _uint16),
    0x05: (1, "motion", lambda d, o: d[o]),
    0x06: (2, "co2", _uint16),
    0x07: (2, "vdd", _uint16),
    0x08: (2, "analog1", _uint16),
    0x09: (6, "position", None),
    0x0A: (2, "pulse1", _uint16),
    0x0B: (4, "pulse1_absolute", _uint32),
    0x0C: (2, "external_temperature", lambda d, o: _int16(d, o) / 10),
    0x0D: (1, "external_digital", lambda d, o: d[o]),
    0x0E: (2, "external_distance", _uint16),
    0x0F: (1, "acceleration_motion", lambda d, o: d[o]),
    0x10: (4, "ir_temperature", None),
    0x11: (1, "occupancy", lambda d, o: d[o]),
    0x12: (1, "waterleak", lambda d, o: d[o]),
    0x13: (65, "room_ir_temperature", _room_ir),
    0x14: (4, "pressure", lambda d, o: _uint32(d, o) / 1000),
    0x15: (2, "sound", None),
    0x16: (2, "pulse2", _uint16),
    0x17: (4, "pulse2_absolute", _uint32),
    0x18: (2, "analog2", _uint16),
    0x19: (2, "external_temperature_2", lambda d, o: _int16(d, o) / 10),
    0x1A: (1, "external_digital2", lambda d, o: d[o]),
    0x1B: (4, "external_analog_uv", _int32),
    0x1C: (2, "tvoc", _uint16),
    0x1D: (1, "iaq", lambda d, o: d[o]),
    0x1E: (1, "generic_bool", lambda d, o: bool(d[o])),
    0x1F: (1, "generic_int8", lambda d, o: d[o]),
    0x20: (2, "generic_int16", _uint16),
    0x21: (1, "view", lambda d, o: d[o]),
    0x22: (2, "setpoint", lambda d, o: _int16(d, o) / 10),
    0x23: (1, "speed", lambda d, o: d[o]),
    0x24: (1, "external_humidity", lambda d, o: d[o]),
    0x3D: (4, "debug", None),
}


def decode_elsys(data: bytes) -> DecodedPayload:
    """Decode one ELSYS uplink; malformed frames raise ValueError."""
    measurements: list[Measurement] = []
    offset = 0
    while offset < len(data):
        type_byte = data[offset]
        type_code = type_byte & 0x3F
        timestamp_size = _TIMESTAMP_SIZES[type_byte >> 6]
        entry = _TYPES.get(type_code)
        if entry is None:
            break
        length, name, factory = entry
        value_offset = offset + 1
        value_end = value_offset + length
        timestamp_offset = value_end
        if timestamp_offset + timestamp_size > len(data):
            raise ValueError(
                f"Measurement 0x{type_code:02X} requires "
                f"{length + timestamp_size} value bytes, got "
                f"{len(data) - value_offset}"
            )
        timestamp: Timestamp = None
        if timestamp_size:
            timestamp = int.from_bytes(
                data[timestamp_offset : timestamp_offset + timestamp_size], "big"
            )
        if type_code == 0x03:
            measurements.extend(
                (
                    Measurement("acceleration_x", _int8(data, value_offset), timestamp),
                    Measurement(
                        "acceleration_y", _int8(data, value_offset + 1), timestamp
                    ),
                    Measurement(
                        "acceleration_z", _int8(data, value_offset + 2), timestamp
                    ),
                )
            )
        elif type_code == 0x09:
            measurements.extend(
                (
                    Measurement(
                        "latitude", _int24(data, value_offset) / 10000, timestamp
                    ),
                    Measurement(
                        "longitude",
                        _int24(data, value_offset + 3) / 10000,
                        timestamp,
                    ),
                )
            )
        elif type_code == 0x10:
            measurements.extend(
                (
                    Measurement(
                        "ir_internal_temperature",
                        _int16(data, value_offset) / 10,
                        timestamp,
                    ),
                    Measurement(
                        "ir_target_temperature",
                        _int16(data, value_offset + 2) / 10,
                        timestamp,
                    ),
                )
            )
        elif type_code == 0x15:
            measurements.extend(
                (
                    Measurement("sound_peak", data[value_offset], timestamp),
                    Measurement("sound_avg", data[value_offset + 1], timestamp),
                )
            )
        elif type_code == 0x3D:
            measurements.append(
                Measurement(
                    "debug",
                    _uint32(data, value_offset),
                    timestamp,
                    attributes={
                        "source": data[value_offset],
                        "error_code_1": data[value_offset + 1],
                        "error_code_2": data[value_offset + 2],
                        "error_code_3": data[value_offset + 3],
                    },
                )
            )
        else:
            assert factory is not None
            measurements.append(
                Measurement(name, factory(data, value_offset), timestamp)
            )
        offset = timestamp_offset + timestamp_size
    return DecodedPayload(measurements=measurements)
