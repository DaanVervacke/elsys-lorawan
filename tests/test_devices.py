"""Feed uplinks through live device models and verify merged state."""

from datetime import UTC, datetime, timedelta

from lorawan_connection import DeviceDescriptor, UplinkEvent

from elsys_lorawan import (
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


def make_device(model, stack: str = "tts"):
    brand_id, model_id = model.identifiers.get(stack, ("elsys", "unknown"))
    descriptor = DeviceDescriptor(
        network_id="network",
        dev_eui="0201010101010101",
        name="Device",
        application_id="application",
        profile_id="profile",
        stack=stack,
        brand_id=brand_id,
        model_id=model_id,
    )
    return model(descriptor)


def uplink(device, data: bytes, port: int = 1, received_at=None):
    device._receive_event(
        UplinkEvent(
            descriptor=device.descriptor,
            received_at=received_at or datetime(2026, 10, 8, tzinfo=UTC),
            f_port=port,
            data=data,
        )
    )


def test_ers_updates():
    device = make_device(ERS)
    uplink(device, bytes.fromhex("01 00 E2 02 29 04 00 27 05 06"))
    assert device.temperature == 22.6
    assert device.humidity == 41
    assert device.light == 39
    assert device.motion == 6
    # stale reading does not replace newer value
    uplink(
        device,
        bytes.fromhex("01 00 E2 02 29 04 00 27 05 06"),
        received_at=device._times["temperature"] - timedelta(seconds=1),
    )
    assert device.temperature == 22.6
    # wrong port is ignored
    uplink(device, bytes.fromhex("01 00 FA 04 00 27 05 06"), port=99)
    assert device.temperature == 22.6
    # malformed frame is discarded atomically
    uplink(device, bytes.fromhex("01 00"))
    assert device.temperature == 22.6
    device.close()
    uplink(device, bytes.fromhex("01 00 FA"))
    assert device.temperature == 22.6


def test_ers_co2_updates():
    device = make_device(ERSCO2)
    uplink(device, bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 06 03 08"))
    assert device.temperature == 22.6
    assert device.co2 == 776
    device.close()


def test_ers_co2_lite_updates():
    device = make_device(ERSCO2Lite)
    uplink(device, bytes.fromhex("01 00 E2 02 29 06 03 08"))
    assert device.temperature == 22.6
    assert device.co2 == 776
    assert device.light is None
    device.close()


def test_ers_lite_updates():
    device = make_device(ERSLite)
    uplink(device, bytes.fromhex("01 00 E2 02 29"))
    assert device.temperature == 22.6
    assert device.humidity == 41
    device.close()


def test_ers_voc_updates():
    device = make_device(ERSVOC)
    uplink(device, bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 1C 01 F4"))
    assert device.temperature == 22.6
    assert device.tvoc == 500
    device.close()


def test_ers_sound_updates():
    device = make_device(ERSSound)
    uplink(device, bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 15 01 01"))
    assert device.sound_peak == 1
    assert device.sound_avg == 1
    device.close()


def test_ers_eye_updates():
    device = make_device(ERSEye)
    uplink(device, bytes.fromhex("01 00 E2 02 29 04 00 27 05 06 11 01"))
    assert device.occupancy == 1
    device.close()


def test_elt_2_updates():
    device = make_device(ELT2)
    uplink(device, bytes.fromhex("01 00 E2 02 29 03 01 27 05 14 06 01 01 11"))
    assert device.temperature == 22.6
    assert device.acceleration_x == 1
    assert device.acceleration_y == 39
    assert device.acceleration_z == 5
    assert device.pressure == 100729.105
    device.close()


def test_elt_lite_updates():
    device = make_device(ELTLite)
    uplink(device, bytes.fromhex("01 00 E2 02 29"))
    assert device.temperature == 22.6
    device.close()


def test_elt_ultrasonic_updates():
    device = make_device(ELTUltrasonic)
    uplink(
        device,
        bytes.fromhex("01 00 E2 02 29 03 01 27 05 14 06 01 01 11 0E 23 11"),
    )
    assert device.external_distance == 8977
    device.close()


def test_ems_updates():
    device = make_device(EMS)
    uplink(
        device,
        bytes.fromhex("01 00 E2 02 29 03 01 27 05 0A 11 01 12 11 0A 21 11"),
    )
    assert device.temperature == 22.6
    assert device.waterleak == 17
    device.close()


def test_ems_door_updates():
    device = make_device(EMSDoor)
    uplink(device, bytes.fromhex("03 01 27 05 0A 11 01 0B 00 0A 00 11"))
    assert device.acceleration_x == 1
    assert device.motion is None
    device.close()


def test_ems_lite_updates():
    device = make_device(EMSLite)
    uplink(device, bytes.fromhex("01 00 E2 02 29 12 11"))
    assert device.waterleak == 17
    device.close()


def test_ems_desk_updates():
    device = make_device(EMSDesk)
    uplink(device, bytes.fromhex("01 00 E2 02 29 03 01 27 05 11 02"))
    assert device.occupancy == 2
    device.close()
