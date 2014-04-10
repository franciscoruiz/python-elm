from unittest.case import skipIf

from nose.tools import assert_dict_contains_subset
from nose.tools import assert_in
from nose.tools import assert_is_instance
from nose.tools import assert_is_none
from nose.tools import eq_
from serial.serialutil import SerialException
from serial.tools.list_ports import comports

from elm327.connection import SerialConnection


_are_serial_ports_available = bool(comports())
_skip_if_no_ports = \
    skipIf(not _are_serial_ports_available, 'No serial port available')


class TestSerialConnection(object):

    def setup(self):
        connection_class = _get_serial_connection()
        self.connection = connection_class.connect("/dev/pts/1")
        self.mock_port = self.connection._port

    def test_initialization(self):
        port = _MockSerialPort()
        connection = SerialConnection(port)

        eq_(port, connection._port)

    def test_closing(self):
        self.connection.close()

        assert_is_none(self.connection._port)
        self.mock_port._assert_method_was_called("close")

    #{ Connection tests

    def test_connecting_to_existing_device(self):
        connection_class = _get_serial_connection()
        connection = connection_class.connect("/dev/pts/1")

        assert_is_instance(connection, connection_class)

        mock_port = connection._port
        eq_({"baudrate": 38400}, mock_port.init_kwargs)

    def test_connecting_with_specific_baud_rate(self):
        connection_class = _get_serial_connection()
        connection = connection_class.connect("/dev/pts/1", baudrate=1)

        mock_port = connection._port
        eq_({"baudrate": 1}, mock_port.init_kwargs)

    def test_connecting_with_port_extra_parameters(self):
        connection_class = _get_serial_connection()
        connection = \
            connection_class.connect("/dev/pts/1", 1, "arg1", extra_arg=10)

        mock_port = connection._port
        eq_(("/dev/pts/1", "arg1"), mock_port.init_args)
        assert_dict_contains_subset({"extra_arg": 10}, mock_port.init_kwargs)

    def test_serial_port_error_when_connecting(self):
        port_class = _SerialPortCommunicationError
        connection_class = _get_serial_connection(port_class)
        connection = connection_class.connect("/dev/pts/1")
        eq_(None, connection)

    def test_connecting_to_non_existing_device(self):
        port_class = _SerialPortDeviceNotFoundError
        connection_class = _get_serial_connection(port_class)
        connection = connection_class.connect("/dev/madeup")
        eq_(None, connection)

    #{ Auto-connection tests

    @_skip_if_no_ports
    def test_auto_connecting_with_existing_device(self):
        connection_class = _get_serial_connection()
        connection = connection_class.auto_connect()
        assert_is_instance(connection, connection_class)

    @_skip_if_no_ports
    def test_auto_connecting_with_no_suitable_device_found(self):
        port_class = _SerialPortCommunicationError
        connection_class = _get_serial_connection(port_class)
        connection = connection_class.auto_connect()
        eq_(None, connection)

    def test_auto_connecting_with_device_found(self):
        port_class = _MockSerialPort
        connection_class = _get_serial_connection(port_class)
        connection = connection_class.auto_connect()
        assert_is_instance(connection, connection_class)


def _get_serial_connection(port_class=None):
    port_class = port_class or _MockSerialPort
    connection_subclass = type(
        SerialConnection.__name__,
        (SerialConnection,),
        {"_PORT_CLASS": port_class},
        )
    return connection_subclass


def _mock_method(function):
    function_name = function.func_name
    def decorator(self, *args, **kwargs):
        self._method_calls[function_name] = (args, kwargs)
        result = function(self, *args, **kwargs)
        return result
    return decorator


class _MockSerialPort(object):

    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs

        self._method_calls = {}
        self._commands_sent = []

    def _assert_method_was_called(self, method_name, *args, **kwargs):
        assert_in(
            method_name,
            self._method_calls,
            "Method {!r} was not called".format(method_name),
            )

        actual_method_args = self._method_calls[method_name]
        wrong_arguments_message = \
            "Method {!r} was not called with the expected arguments: " \
            "Expected: {} - " \
            "Actual: {}".format(
                method_name,
                (args, kwargs),
                actual_method_args,
                )
        eq_((args, kwargs), actual_method_args, wrong_arguments_message)

    def _assert_command_was_sent(self, command):
        assert_in(
            command,
            self._commands_sent,
            "Command {!r} was not sent".format(command),
            )

    @_mock_method
    def read(self):
        pass

    @_mock_method
    def write(self, data):
        self._commands_sent.append(data)

    @_mock_method
    def flushOutput(self):
        pass

    @_mock_method
    def flushInput(self):
        pass

    @_mock_method
    def close(self):
        pass


class _SerialPortWithErrorOnInit(object):

    _EXCEPTION_CLASS = SerialException

    def __init__(self, *args, **kwargs):
        raise self._EXCEPTION_CLASS()


class _SerialPortCommunicationError(_SerialPortWithErrorOnInit):

    _EXCEPTION_CLASS = SerialException


class _SerialPortDeviceNotFoundError(_SerialPortWithErrorOnInit):

    _EXCEPTION_CLASS = OSError
