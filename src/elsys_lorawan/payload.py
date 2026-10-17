"""Decoded measurements shared by the ELSYS wire protocol."""

from dataclasses import dataclass, field

type Value = None | bool | int | float | str | list[Value] | dict[str, Value]
type Timestamp = None | int


@dataclass(frozen=True)
class Measurement:
    """A measurement name, its value, and the byte offsets it came from."""

    name: str
    value: Value
    timestamp: Timestamp = None
    attributes: dict[str, Value] = field(default_factory=dict)


@dataclass
class DecodedPayload:
    """Measurements and device metadata from one complete uplink."""

    measurements: list[Measurement] = field(default_factory=list)
    metadata: dict[str, Value] = field(default_factory=dict)
