"""Merge ELSYS uplinks while preserving partial and stale readings."""

from collections.abc import Callable
from datetime import datetime
from typing import ClassVar, override

from lorawan_connection import Device, DeviceDescriptor, DeviceEvent, EventType

from .decoders import decode_elsys
from .payload import DecodedPayload, Measurement, Value

type Decoder = Callable[[bytes], DecodedPayload]


class ElsysDevice(Device):
    """Latest uplink measurements and vendor metadata for one device."""

    _decoder: ClassVar[Decoder] = decode_elsys
    _ports: ClassVar[tuple[int, ...]] = (1,)

    def __init__(self, descriptor: DeviceDescriptor) -> None:
        super().__init__(descriptor)
        self.measurements: dict[str, Measurement] = {}
        self.metadata: dict[str, Value] = {}
        self._times: dict[str, datetime] = {}

    @classmethod
    def decode(cls, data: bytes) -> DecodedPayload:
        """Decode one uplink; malformed frames raise ValueError."""
        return cls._decoder(data)

    def measurement_value(self, name: str) -> Value:
        """Read a measurement value, or None before it arrives."""
        item = self.measurements.get(name)
        return item.value if item is not None else None

    def _number(self, name: str) -> float | None:
        value = self.measurement_value(name)
        return float(value) if isinstance(value, (int, float)) else None

    @property
    def temperature(self) -> float | None:
        """Temperature in degrees Celsius."""
        return self._number("temperature")

    @property
    def humidity(self) -> float | None:
        """Relative humidity in percent."""
        return self._number("humidity")

    @property
    def vdd(self) -> float | None:
        """Battery voltage in millivolts."""
        return self._number("vdd")

    @override
    def handle_event(self, event: DeviceEvent) -> None:
        if (
            self.closed
            or event.type != EventType.UPLINK
            or event.f_port not in self._ports
        ):
            return
        try:
            payload = self.decode(event.data)
        except (ValueError, IndexError):
            return
        changed = False
        timestamp = event.received_at
        for item in payload.measurements:
            if item.name in self._times and timestamp < self._times[item.name]:
                continue
            self._times[item.name] = timestamp
            self.measurements[item.name] = item
            changed = True
        for name, value in payload.metadata.items():
            self.metadata[name] = value
            changed = True
        if changed:
            self.notify()
