"""ELSYS models and official The Things Stack catalog identities."""

from .device import ElsysDevice


class ERS(ElsysDevice):
    """Room sensor with temperature, humidity, light, and PIR motion."""

    identifiers = {"tts": ("elsys", "ers")}

    @property
    def light(self) -> float | None:
        """Light intensity in lux."""
        return self._number("light")

    @property
    def motion(self) -> int | None:
        """Number of motion events since the last uplink."""
        value = self.measurement_value("motion")
        return value if isinstance(value, int) else None


class ERSLite(ERS):
    """Compact room sensor with temperature and humidity."""

    identifiers = {"tts": ("elsys", "ers-lite")}


class ERSCO2(ERS):
    """Room sensor with temperature, humidity, light, motion, and CO2."""

    identifiers = {"tts": ("elsys", "ers-co2")}

    @property
    def co2(self) -> float | None:
        """CO2 concentration in ppm."""
        return self._number("co2")


class ERSCO2Lite(ERSCO2):
    """Compact room sensor with temperature, humidity, and CO2."""

    identifiers = {"tts": ("elsys", "ers-co2-lite")}


class ERSVOC(ERS):
    """Room sensor with temperature, humidity, light, motion, and TVOC."""

    identifiers = {"tts": ("elsys", "ers-voc")}

    @property
    def tvoc(self) -> float | None:
        """Total VOC concentration in ppb."""
        return self._number("tvoc")


class ERSSound(ERS):
    """Room sensor measuring peak and average sound levels."""

    identifiers = {"tts": ("elsys", "ers-sound")}

    @property
    def sound_peak(self) -> float | None:
        """Peak sound level in dB."""
        return self._number("sound_peak")

    @property
    def sound_avg(self) -> float | None:
        """Average sound level in dB."""
        return self._number("sound_avg")


class ERSEye(ERS):
    """Occupancy sensor with Grid-Eye thermal array and PIR motion."""

    identifiers = {"tts": ("elsys", "ers-eye")}

    @property
    def occupancy(self) -> int | None:
        """Occupancy state: 0 unoccupied, 1 pending, 2 occupied."""
        value = self.measurement_value("occupancy")
        return value if isinstance(value, int) else None


class ELT2(ElsysDevice):
    """Multi-sensor with two external sensor inputs."""

    identifiers = {"tts": ("elsys", "elt-2")}

    @property
    def external_temperature(self) -> float | None:
        """External temperature probe in degrees Celsius."""
        return self._number("external_temperature")

    @property
    def external_digital(self) -> bool | None:
        """External digital input state."""
        value = self.measurement_value("external_digital")
        return bool(value) if isinstance(value, int) else None

    @property
    def pulse1(self) -> float | None:
        """Relative pulse count on input 1."""
        return self._number("pulse1")

    @property
    def pressure(self) -> float | None:
        """Barometric pressure in hPa."""
        return self._number("pressure")

    @property
    def acceleration_x(self) -> float | None:
        """X-axis acceleration."""
        return self._number("acceleration_x")

    @property
    def acceleration_y(self) -> float | None:
        """Y-axis acceleration."""
        return self._number("acceleration_y")

    @property
    def acceleration_z(self) -> float | None:
        """Z-axis acceleration."""
        return self._number("acceleration_z")


class ELTLite(ELT2):
    """Compact sensor with internal temperature and humidity."""

    identifiers = {"tts": ("elsys", "elt-lite")}


class ELTUltrasonic(ELT2):
    """Sensor with an ultrasonic distance probe."""

    identifiers = {"tts": ("elsys", "elt-ultrasonic")}

    @property
    def external_distance(self) -> float | None:
        """Measured distance in millimetres."""
        return self._number("external_distance")


class EMS(ElsysDevice):
    """Multi-sensor with temperature, humidity, motion, door, and leak."""

    identifiers = {"tts": ("elsys", "ems")}

    @property
    def motion(self) -> int | None:
        """Number of motion events since the last uplink."""
        value = self.measurement_value("motion")
        return value if isinstance(value, int) else None

    @property
    def waterleak(self) -> float | None:
        """Water leak detection level."""
        return self._number("waterleak")

    @property
    def acceleration_x(self) -> float | None:
        """X-axis acceleration."""
        return self._number("acceleration_x")

    @property
    def acceleration_y(self) -> float | None:
        """Y-axis acceleration."""
        return self._number("acceleration_y")

    @property
    def acceleration_z(self) -> float | None:
        """Z-axis acceleration."""
        return self._number("acceleration_z")


class EMSDoor(EMS):
    """Door activity sensor with accelerometer and reed switch."""

    identifiers = {"tts": ("elsys", "ems-door")}


class EMSLite(EMS):
    """Climate sensor with temperature, humidity, and water leak."""

    identifiers = {"tts": ("elsys", "ems-lite")}


class EMSDesk(EMS):
    """Desk occupancy sensor with IR presence detection."""

    identifiers = {"tts": ("elsys", "ems-desk")}

    @property
    def occupancy(self) -> int | None:
        """Occupancy state: 0 unoccupied, 1 pending, 2 occupied."""
        value = self.measurement_value("occupancy")
        return value if isinstance(value, int) else None
