from datetime import datetime

from nose.tools import assert_almost_equal
from nose.tools import assert_is_instance
from nose.tools import assert_is_none
from nose.tools import assert_raises
from nose.tools import eq_

from elm327.connection import CommandNotSupportedError
from elm327.connection import ELMInterfaceConnection
from elm327.connection import SerialConnection
from elm327.obd import OBDCommand
from elm327.obd import OBDResponse
from tests.utils import MockSerialPort
from tests.utils import MockSerialPortDataReader
from tests.utils import MockSerialPortDataWriter


class TestSerialConnection(object):

    def setup(self):
        self.mock_port = MockSerialPort()
        self.connection = SerialConnection(self.mock_port)

    def test_initialization(self):
        port = MockSerialPort()
        connection = SerialConnection(port)

        eq_(port, connection._port)

    def test_closing(self):
        self.connection.close()

        assert_is_none(self.connection._port)
        self.mock_port.assert_method_was_called("close")

    #{ Communication tests

    def test_sending_command_with_valid_response(self):
        mock_data_reader = MockSerialPortDataReader("a response")
        mock_port = MockSerialPort(reader=mock_data_reader)
        connection = SerialConnection(mock_port)
        response = connection.send_command("a command")

        eq_("a response", response)
        mock_port.assert_scenario(
            ("flushInput", (), {}),
            ("flushOutput", (), {}),
            ("write", ("a command",), {}),
            ("write", ("\n\r",), {}),
            ("read", (1,), {}),
            )

    def test_sending_command_with_delayed_response_reading(self):
        mock_port = _MockSerialPortWithTimings()
        connection = SerialConnection(mock_port)
        response = connection.send_command("a command", read_delay=1)

        mock_port.assert_data_was_written("a command")
        mock_port.assert_data_was_read(response)

        actual_delay = mock_port._last_read_time - mock_port._last_write_time
        assert_almost_equal(1, actual_delay.total_seconds(), 0)

    def test_characters_beyond_prompt_in_response_to_command(self):
        """
        Once the prompt/terminator is read, no further reading is performed.

        """
        mock_data_reader = MockSerialPortDataReader("ab>ef")
        mock_port = MockSerialPort(reader=mock_data_reader)
        connection = SerialConnection(mock_port)
        response = connection.send_command("a command")

        eq_("ab", response)
        mock_port.assert_scenario(
            ("flushInput", (), {}),
            ("flushOutput", (), {}),
            ("write", ("a command",), {}),
            ("write", ("\n\r",), {}),
            ("read", (1,), {}),
            ("read", (1,), {}),
            ("read", (1,), {}),
            )

    def test_null_characters_in_response_to_command(self):
        """NULL characters received in the response are ignored"""
        mock_data_reader = MockSerialPortDataReader("ab c\x00d ef>")
        mock_port = MockSerialPort(reader=mock_data_reader)
        connection = SerialConnection(mock_port)
        response = connection.send_command("a command")

        eq_("ab cd ef", response)


class _MockSerialPortWithTimings(MockSerialPort):

    def __init__(self, *args, **kwargs):
        super(_MockSerialPortWithTimings, self).__init__(*args, **kwargs)

        self._last_read_time = None
        self._last_write_time = None

    def read(self, *args, **kwargs):
        self._last_read_time = datetime.now()
        return super(_MockSerialPortWithTimings, self).read(*args, **kwargs)

    def write(self, data):
        super(_MockSerialPortWithTimings, self).write(data)
        self._last_write_time = datetime.now()


class TestELMInterfaceConnection(object):

    def test_sending_obd_commands(self):
        command = OBDCommand(0x01, 0x00)

        mock_port = _MockOBDPort({
            command: "41 00 01 23 45 67"
            })
        connection = ELMInterfaceConnection(mock_port)
        mock_port.clear_data()

        response = connection.send_obd_command(command)

        mock_port.assert_data_was_written("01 00")

        assert_is_instance(response, OBDResponse)
        eq_((1, 35, 69, 103), response.raw_data)

    def test_sending_non_explicitly_unsupported_pid_command(self):
        command = OBDCommand(0x01, 0x01)
        mock_port = _MockOBDPort({
            command: "?",
            })
        connection = ELMInterfaceConnection(mock_port)
        with assert_raises(CommandNotSupportedError):
            connection.send_obd_command(command)

        mock_port.clear_data()

        with assert_raises(CommandNotSupportedError):
            connection.send_obd_command(command)

        mock_port.assert_no_data_was_written()


class _MockOBDPort(MockSerialPort):

    def __init__(self, scenario):
        responses_by_command = \
            {' '.join(c.to_hex_words()): r for c, r in scenario.items()}
        reader = writer = _WriterReader(responses_by_command)
        super(_MockOBDPort, self).__init__(writer, reader)


class _WriterReader(MockSerialPortDataWriter, MockSerialPortDataReader):

    def __init__(self, responses_by_command):
        MockSerialPortDataWriter.__init__(self)
        MockSerialPortDataReader.__init__(self)

        self._responses_by_command = responses_by_command

    def write(self, data):
        MockSerialPortDataWriter.write(self, data)
        try:
            expected_response = self._responses_by_command[data]
        except KeyError:
            pass
        else:
            self._set_expected_data(expected_response)
