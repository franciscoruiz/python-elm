from nose.tools import assert_false
from nose.tools import assert_is_none
from nose.tools import assert_raises
from nose.tools import eq_
from nose.tools import ok_

from elm327.obd import OBDCommand
from elm327.obd import OBDInterface
from elm327.obd import ValueNotAvailableError
from elm327.pcm_values import NumericValueParser
from elm327.pcm_values import PCMValue
from elm327.pcm_values import PCMValueDefinition
from elm327.pcm_values import PERCENTAGE_VALUE_PARSER
from elm327.pcm_values import EnumeratedValueParser
from elm327.pcm_values import BitwiseEncodedValueParser


_STUB_OBD_COMMAND = OBDCommand(0x01, 0x10)


_STUB_PCM_VALUE_DEFINITION = PCMValueDefinition(
    _STUB_OBD_COMMAND,
    NumericValueParser(),
    )


class TestOBDCommand(object):

    def test_conversion_to_hex_words(self):
        hex_words = _STUB_OBD_COMMAND.to_hex_words()
        eq_(("01", "10"), hex_words)

    def test_conversion_to_pretty_hex_words(self):
        hex_words = _STUB_OBD_COMMAND.to_hex_words(True)
        eq_(("0x01", "0x10"), hex_words)

    def test_repr(self):
        eq_("OBDCommand(mode=0x01, pid=0x10)", repr(_STUB_OBD_COMMAND))

    def test_equality(self):
        ok_(_STUB_OBD_COMMAND == _STUB_OBD_COMMAND)
        ok_(_STUB_OBD_COMMAND == OBDCommand(_STUB_OBD_COMMAND.mode, _STUB_OBD_COMMAND.pid))

        assert_false(_STUB_OBD_COMMAND == OBDCommand(_STUB_OBD_COMMAND.mode, 0xAA))
        assert_false(_STUB_OBD_COMMAND == OBDCommand(0xAA, _STUB_OBD_COMMAND.pid))

        assert_false(_STUB_OBD_COMMAND == None)

    def test_hash(self):
        eq_(hash(_STUB_OBD_COMMAND), hash(_STUB_OBD_COMMAND))


class TestOBDInterface(object):

    def test_numeric_value(self):
        pcm_value_definition = PCMValueDefinition(
            _STUB_OBD_COMMAND,
            NumericValueParser("rpm", value_scaler=lambda v: v / 4)
            )
        self._test_pcm_value_reading(
            pcm_value_definition,
            "01 23",
            PCMValue(72, unit="rpm"),
            )

    def test_percentage_value(self):
        pcm_value_definition = PCMValueDefinition(
            _STUB_OBD_COMMAND,
            PERCENTAGE_VALUE_PARSER,
            )
        self._test_pcm_value_reading(
            pcm_value_definition,
            "00 23",
            PCMValue(3500, unit="%"),
            )

    def test_enumerated_value(self):
        enumeration = [None] * 512
        enumeration[255] = "A value"
        pcm_value_definition = PCMValueDefinition(
            _STUB_OBD_COMMAND,
            EnumeratedValueParser(enumeration),
            )
        self._test_pcm_value_reading(
            pcm_value_definition,
            "00 FF",
            PCMValue("A value"),
            )

    def test_bitwise_encoded_value(self):
        pcm_value_definition = PCMValueDefinition(
            _STUB_OBD_COMMAND,
            BitwiseEncodedValueParser({0: "N/A", 255: "Gasoline"}),
            )
        self._test_pcm_value_reading(
            pcm_value_definition,
            "00 FF",
            PCMValue("Gasoline"),
            )

    @staticmethod
    def _test_pcm_value_reading(pcm_value_definition, raw_data, expected_value):
        command = pcm_value_definition.command
        command_response = _make_response_for_command(command, raw_data)
        connection = _ConstantResponseConnection(command_response)

        interface = OBDInterface(connection)

        actual_value = interface.read_pcm_value(pcm_value_definition)

        eq_(expected_value, actual_value)

    def test_no_data_received(self):
        connection = _ConstantResponseConnection("NO DATA")
        interface = OBDInterface(connection)

        value = interface.read_pcm_value(_STUB_PCM_VALUE_DEFINITION)
        assert_is_none(value)

    def test_unavailable_pcm_value(self):
        """
        Attempting to read unavailable (unsupported but not explicitly) values
        causes an error, but several readings don't hit the connection.

        """
        connection = _ConstantResponseConnection("?")
        interface = OBDInterface(connection)

        with assert_raises(ValueNotAvailableError):
            interface.read_pcm_value(_STUB_PCM_VALUE_DEFINITION)

        with assert_raises(ValueNotAvailableError):
            interface.read_pcm_value(_STUB_PCM_VALUE_DEFINITION)

        connection.assert_read_values_count_eq(1)

    def test_unsupported_pcm_value(self):
        """
        Attempting to read (explicitly) unsupported values causes an error.

        """
        connection = _NoValueSupportedConnection()
        interface = OBDInterface(connection)

        with assert_raises(ValueNotAvailableError):
            interface.read_pcm_value(_STUB_PCM_VALUE_DEFINITION)


class _ConstantResponseConnection(object):

    def __init__(self, raw_response):
        self._raw_response = raw_response

        self._commands_sent_count = 0

    def send_command(self, command, read_delay=None):
        # Ignore AT commands
        if command.startswith("AT"):
            return ""

        self._commands_sent_count += 1
        return self._raw_response

    def assert_read_values_count_eq(self, expected_count):
        eq_(expected_count, self._commands_sent_count)


class _NoValueSupportedConnection(object):

    def send_command(self, command, read_delay=None):
        if command == OBDCommand(0x01, 0x00):
            return "0"

        return ""

def _make_response_for_command(command, response_data):
    return "{} {} {}".format(command.mode, command.pid, response_data)
