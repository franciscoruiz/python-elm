# coding: utf-8
from elm327.obd import OBDCommand


class PCMValueDefinition(object):

    def __init__(self, command, parser):
        self.command = command
        self.parser = parser


class PCMValue(object):

    def __init__(self, value, unit=None):
        self.value = value
        self.unit = unit

    def __eq__(self, other):
        try:
            other_value, other_unit = other.value, other.unit
        except AttributeError:
            return NotImplemented

        return self.value == other_value and self.unit == other_unit

    def __repr__(self):
        return "{}(value={}, unit={})".format(
            self.__class__.__name__,
            self.value,
            self.unit,
            )


class EnumeratedValueParser(object):

    def __init__(self, enumeration):
        self._enumeration = enumeration

    def __call__(self, response_bytes):
        numeric_value = _parse_bytes(response_bytes)
        value = self._enumeration[numeric_value]
        return PCMValue(value)


class BitwiseEncodedValueParser(object):

    def __init__(self, mapping):
        self._mapping = mapping

    def __call__(self, response_bytes):
        numeric_value = _parse_bytes(response_bytes)
        value = self._mapping[numeric_value]
        return PCMValue(value)


class NumericValueParser(object):

    def __init__(self, unit=None, value_scaler=None):
        self.unit = unit
        self._value_scaler = value_scaler

    def __call__(self, response_bytes):
        value = _parse_bytes(response_bytes)
        if self._value_scaler:
            value = self._value_scaler(value)
        return PCMValue(value, self.unit)


def _parse_bytes(response_bytes):
    result = 0
    response_bytes_reversed = reversed(response_bytes)
    for byte_offset, byte in enumerate(response_bytes_reversed):
        result += byte * pow(256, byte_offset)
    return result


PERCENTAGE_VALUE_PARSER = NumericValueParser(
    value_scaler=lambda v: v * 100,
    unit="%",
    )


# { Values


FUEL_LEVEL = PCMValueDefinition(
    OBDCommand(0x01, 0x2F),
    PERCENTAGE_VALUE_PARSER,
    )

FUEL_TYPE = PCMValueDefinition(
    OBDCommand(0x01, 0x51),
    EnumeratedValueParser({
        # 1 byte
        0: "Not available",
        1: "Gasoline",
        2: "Methanol",
        3: "Ethanol",
        4: "Diesel",
        5: "LPG",
        6: "CNG",
        7: "Propane",
        8: "Electric",
        9: "Bifuel running Gasoline",
        10: "Bifuel running Methanol",
        11: "Bifuel running Ethanol",
        12: "Bifuel running LPG",
        13: "Bifuel running CNG",
        14: "Bifuel running Propane",
        15: "Bifuel running Electricity",
        16: "Bifuel running electric and combustion engine",
        17: "Hybrid gasoline",
        18: "Hybrid Ethanol",
        19: "Hybrid Diesel",
        20: "Hybrid Electric",
        21: "Hybrid running electric and combustion engine",
        22: "Hybrid Regenerative",
        23: "Bifuel running diesel",
        })
    )

ENGINE_FUEL_RATE = PCMValueDefinition(
    OBDCommand(0x01, 0x5E),
    NumericValueParser(unit="L/h", value_scaler=lambda v: v * 0.05),
    )

VEHICLE_SPEED = PCMValueDefinition(
    OBDCommand(0x01, 0x0D),
    NumericValueParser(unit="km/h"),
    )

ENGINE_RPM = PCMValueDefinition(
    OBDCommand(0x01, 0x0C),
    NumericValueParser(unit="rpm", value_scaler=lambda v: v / 4),
    )

ENGINE_COOLANT_TEMPERATURE = PCMValueDefinition(
    OBDCommand(0x01, 0x05),
    NumericValueParser(unit="°C", value_scaler=lambda v: v - 40),
    )
