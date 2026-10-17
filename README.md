# elsys-lorawan

ELSYS LoRaWAN device models and command-line reader, built on
[lorawan-connection](https://pypi.org/project/lorawan-connection/).

All ELSYS devices share a single TLV uplink payload: each measurement
is a 1-byte type code followed by a fixed-length value. This package
decodes that payload for every supported model and exposes the readings
as typed Python properties.

## Supported devices

| Model          | TTS model id     | Typical measurements                                   |
| -------------- | ---------------- | ------------------------------------------------------ |
| ERS            | `ers`            | temperature, humidity, light, motion                    |
| ERS Lite       | `ers-lite`       | temperature, humidity                                   |
| ERS CO2        | `ers-co2`        | temperature, humidity, light, motion, co2               |
| ERS CO2 Lite   | `ers-co2-lite`   | temperature, humidity, co2                             |
| ERS VOC        | `ers-voc`        | temperature, humidity, light, motion, tvoc              |
| ERS Sound      | `ers-sound`      | temperature, humidity, light, motion, sound             |
| ERS Eye        | `ers-eye`        | temperature, humidity, light, motion, occupancy         |
| ELT-2          | `elt-2`          | temperature, humidity, acceleration, external inputs     |
| ELT Lite       | `elt-lite`       | temperature, humidity                                   |
| ELT Ultrasonic | `elt-ultrasonic` | temperature, humidity, external distance              |
| EMS            | `ems`            | temperature, humidity, motion, waterleak               |
| EMS Door       | `ems-door`       | acceleration, pulse counts                              |
| EMS Lite       | `ems-lite`       | temperature, humidity, waterleak                        |
| EMS Desk       | `ems-desk`       | temperature, humidity, occupancy                        |

Models are discovered through their The Things Stack catalog identities
(brand `elsys`). Every model decodes uplinks received on FPort 1.

## Command line

Install with a backend extra, then run:

```sh
pip install elsys-lorawan[tts]
elsys-lorawan --backend tts --server https://example.com \
  --api-key-file key.txt --list --json
```

Use `--backend chirpstack` with the `chirpstack` extra for ChirpStack.
Run `elsys-lorawan --help` for all options.

## Python usage

```python
from elsys_lorawan import ERSCO2, decode_elsys

print(decode_elsys(bytes.fromhex("01 00 E2 02 29 06 03 08")))
# temperature: 22.6 °C, humidity: 41 %, co2: 776 ppm

device = ERSCO2(descriptor)
device.subscribe(lambda device: print(device.co2))
device.handle_event(uplink_event)
print(device.temperature, device.humidity, device.co2)
```

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv build
```
