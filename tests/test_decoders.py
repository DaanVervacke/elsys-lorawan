"""Decode uplinks against vectors pinned from ELSYS's official codecs."""

import pytest

from elsys_lorawan import decode_elsys


def values(data: bytes) -> dict[str, object]:
    return {item.name: item.value for item in decode_elsys(data).measurements}


class TestOfficialCodecVectors:
    """Examples embedded in TheThingsNetwork lorawan-devices vendor/elsys."""

    def test_ers(self):
        result = values(bytes.fromhex("01 00 E2 02 29 04 00 27 05 06"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["light"] == 39
        assert result["motion"] == 6

    def test_ers_lite(self):
        result = values(bytes.fromhex("01 00 E2 02 29"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41

    def test_ers_co2(self):
        result = values(bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 06 03 08"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["light"] == 39
        assert result["motion"] == 6
        assert result["co2"] == 776

    def test_ers_co2_lite(self):
        result = values(bytes.fromhex("01 00 E2 02 29 06 03 08"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["co2"] == 776

    def test_ers_eye(self):
        result = values(bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 11 01"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["light"] == 39
        assert result["motion"] == 6
        assert result["occupancy"] == 1

    def test_ers_sound(self):
        result = values(bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 15 01 01"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["light"] == 39
        assert result["motion"] == 6
        assert result["sound_peak"] == 1
        assert result["sound_avg"] == 1

    def test_elt_2(self):
        result = values(bytes.fromhex("01 00 E2 02 29 03 01 27 05 14 06 01 01 11"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["acceleration_x"] == 1
        assert result["acceleration_y"] == 39
        assert result["acceleration_z"] == 5
        assert result["pressure"] == 100729.105

    def test_elt_ultrasonic(self):
        result = values(
            bytes.fromhex("01 00 E2 02 29 03 01 27 05 14 06 01 01 11 0E 23 11")
        )
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["pressure"] == 100729.105
        assert result["external_distance"] == 8977

    def test_ems(self):
        result = values(
            bytes.fromhex("01 00 E2 02 29 03 01 27 05 0A 11 01 12 11 0A 21 11")
        )
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["waterleak"] == 17
        assert result["pulse1"] == 8465

    def test_ems_desk(self):
        result = values(bytes.fromhex("01 00 E2 02 29 03 01 27 05 11 02"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["occupancy"] == 2

    def test_ems_door(self):
        result = values(bytes.fromhex("03 01 27 05 0A 11 01 0B 00 0A 00 11"))
        assert result["acceleration_x"] == 1
        assert result["acceleration_y"] == 39
        assert result["acceleration_z"] == 5
        assert result["pulse1"] == 4353
        assert result["pulse1_absolute"] == 655377

    def test_ems_lite(self):
        result = values(bytes.fromhex("01 00 E2 02 29 12 11"))
        assert result["temperature"] == 22.6
        assert result["humidity"] == 41
        assert result["waterleak"] == 17


class TestExtendedTypes:
    """Types documented in the ELSYS uplink application note."""

    def test_negative_temperature(self):
        result = values(bytes.fromhex("01 FF D8"))
        assert result["temperature"] == -4.0

    def test_vdd(self):
        result = values(bytes.fromhex("07 0C 1C"))
        assert result["vdd"] == 3100

    def test_absolute_pulse_count(self):
        result = values(bytes.fromhex("0B 12 34 56 78"))
        assert result["pulse1_absolute"] == 305419896

    def test_external_temperature(self):
        result = values(bytes.fromhex("0C 00 C8"))
        assert result["external_temperature"] == 20.0

    def test_external_analog_uv_signed(self):
        result = values(bytes.fromhex("1B FF FF FF FF"))
        assert result["external_analog_uv"] == -1

    def test_tvoc(self):
        result = values(bytes.fromhex("1C 01 F4"))
        assert result["tvoc"] == 500

    def test_iaq(self):
        result = values(bytes.fromhex("1D 5A"))
        assert result["iaq"] == 90

    def test_pressure(self):
        result = values(bytes.fromhex("14 00 00 27 10"))
        assert result["pressure"] == 10.0

    def test_gps_position(self):
        result = values(bytes.fromhex("09 08 CE 22 01 D3 73"))
        assert result["latitude"] == 57.7058
        assert result["longitude"] == 11.9667

    def test_timestamped_temperature(self):
        items = decode_elsys(bytes.fromhex("41 00 CE 0A")).measurements
        assert items[0].name == "temperature"
        assert items[0].value == 20.6
        assert items[0].timestamp == 10

    def test_later_same_type_overwrites(self):
        result = values(bytes.fromhex("01 00 E2 01 00 FA"))
        assert result["temperature"] == 25.0


class TestMalformedFrames:
    def test_empty_payload(self):
        assert decode_elsys(b"").measurements == []

    def test_truncated_value_raises(self):
        with pytest.raises(ValueError, match="requires"):
            decode_elsys(bytes.fromhex("01 00"))

    def test_unknown_type_stops_parsing(self):
        result = values(bytes.fromhex("01 00 E2 3F 02 29"))
        assert result == {"temperature": 22.6}

    def test_unknown_type_only(self):
        assert decode_elsys(bytes.fromhex("7F")).measurements == []
