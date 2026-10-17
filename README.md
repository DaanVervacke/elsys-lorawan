# elsys-lorawan

Read ELSYS sensors through ChirpStack or The Things Stack using
[`lorawan-connection`](https://github.com/home-assistant-libs/lorawan-connection).

| Model | Readings | Automatic discovery |
| --- | --- | --- |
| ERS | Temperature, humidity, light, motion | TTS |
| ERS Lite | Temperature, humidity | TTS |
| ERS CO2 | Temperature, humidity, light, motion, CO2 | TTS |
| ERS CO2 Lite | Temperature, humidity, CO2 | TTS |
| ERS VOC | Temperature, humidity, light, motion, TVOC | TTS |
| ERS Sound | Temperature, humidity, light, motion, sound peak/average | TTS |
| ERS Eye | Temperature, humidity, light, motion, occupancy | TTS |
| ELT-2 | Temperature, humidity, acceleration, external temperature/digital, pulse, pressure | TTS |
| ELT Lite | Temperature, humidity | TTS |
| ELT Ultrasonic | Temperature, humidity, external distance | TTS |
| EMS | Temperature, humidity, motion, acceleration, water leak, pulse | TTS |
| EMS Door | Acceleration, pulse counts | TTS |
| EMS Lite | Temperature, humidity, water leak | TTS |
| EMS Desk | Temperature, humidity, occupancy | TTS |

Every ELSYS device shares one TLV uplink payload: each measurement is a 1-byte
type code followed by a fixed-length value, optionally timestamped. Coverage
follows the ELSYS
[uplink payload application note](https://elsys.se/public/app_notes/AppNote_ELSYS_uplink_payload.pdf)
and the official payload decoder, with test vectors pinned to the codec examples
in TheThingsNetwork's lorawan-devices repository. The ChirpStack device-profile
catalog lists ELSYS without a numeric vendor id, so there are no ChirpStack
discovery identities; use the models directly, or subclass them with your
deployment's model identity. Sensor data arrives on FPort 1; port 0/mac-layer
events never reach the decoder. This library decodes uplinks and does not
implement device configuration commands.

Raw payloads are decoded locally; a server-side payload formatter is not required.

## Command-line reader

The `elsys-lorawan` command lists devices or prints readings as they arrive.
Install [uv](https://docs.astral.sh/uv/getting-started/installation/) to run it
with `uvx`, or use `pip install "elsys-lorawan[tts]"` for The Things Stack.

### The Things Stack

Use the Application Server gRPC endpoint and an application API key with device
read and application traffic read rights. Specify each application explicitly.

```sh
export TTS_API_KEY="your-api-key"
uvx --from "elsys-lorawan[tts]" elsys-lorawan \
  --backend tts \
  --server https://eu1.cloud.thethings.network:8884 \
  --identity-server https://eu1.cloud.thethings.network:8884 \
  --application YOUR_APPLICATION_ID
```

Set `--identity-server` to your deployment's Identity Server if it differs from
the Application Server. Repeat `--application` for multiple applications.

Add `--list` to print the current devices and exit, or `--json` for
newline-delimited JSON output. Use `--api-key-file /path/to/key` instead of an
environment variable if preferred. Stop watching with Ctrl+C. Run
`elsys-lorawan --help` for all options.

With a pip installation, use `elsys-lorawan` directly in place of the
`uvx --from ... elsys-lorawan` prefix. `python -m elsys_lorawan` also works.

## Python

```python
from lorawan_connection.backend.tts import TTSConnection
from elsys_lorawan import ElsysDeviceCollection


async def list_sensors(endpoint: str, api_key: str, application: str) -> None:
    connection = TTSConnection(
        endpoint,
        api_key,
        identity_server=endpoint,
        application_ids=[application],
        network_id=endpoint,
    )
    devices = ElsysDeviceCollection(connection)
    try:
        await connection.async_connect()
        await devices.async_setup()
        for device in devices.devices.values():
            print(device.descriptor.name, type(device).__name__)
    finally:
        devices.close()
        await connection.close()
```

The collection also accepts a `ChirpStackConnection`. Subscribe with
`devices.subscribe_device_added(listener)` and `device.add_update_listener(listener)`
to receive live readings. Values remain `None` until the sensor reports them.

### Reading measurements

Existing properties such as `ERS.temperature`, `ERS.humidity`, and `ERSCO2.co2`
remain available. All models also expose `measurements[name]`, whose
`Measurement` contains `value`, `timestamp`, and `attributes`. Timestamps are
seconds-ago values when the device transmits timestamped measurements; otherwise
they are `None`. Use `device.measurement_value(name)` for direct access.

```python
from elsys_lorawan import decode_elsys

payload = decode_elsys(bytes.fromhex("0100E202290400270506"))
for measurement in payload.measurements:
    print(measurement.name, measurement.value)
# temperature 22.6
# humidity 41
# light 39
# motion 6
```

Multi-value types split into named measurements: acceleration into
`acceleration_x/y/z`, position into `latitude`/`longitude`, IR temperature into
`ir_internal_temperature`/`ir_target_temperature`, and sound into
`sound_peak`/`sound_avg`. A later measurement of the same type replaces an
earlier one in the same uplink. Direct decoding raises `ValueError` for
truncated values. Live models discard those payloads atomically. Partial updates
retain other readings; older readings cannot replace newer values of the same
measurement. Unknown type codes stop the parse, keeping already-decoded
measurements, matching the official decoder.

## Development

```sh
uv sync
uv run pytest
uv run ruff check .
uv run mypy
uv build
```

Tests include the official codec examples from TheThingsNetwork's
lorawan-devices repository, extended-type and timestamped-measurement coverage,
and malformed-frame cases.

## Releases

The source version stays `0.0.0`. Publishing a GitHub release named `0.1.0`, for
example, builds that version and publishes it to PyPI through Trusted Publishing.
See [RELEASING.md](RELEASING.md) for the one-time publisher setup.

## License

Apache-2.0. Ported from ELSYS's public payload decoder and
[uplink payload application note](https://elsys.se/public/app_notes/AppNote_ELSYS_uplink_payload.pdf).
