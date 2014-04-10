from nose.tools import assert_dict_contains_subset
from nose.tools import assert_in
from nose.tools import assert_is_instance
from nose.tools import assert_is_none
from nose.tools import eq_
from serial.serialutil import SerialException

from elm327.connection import SerialConnection
from elm327.connection import SerialConnectionFactory


class TestSerialConnectionFactory(object):

    def setup(self):
        self.available_port = ('/dev/pts/1', 'pts1', 'HardCodedPort')
        self.factory = SerialConnectionFactory(
            _MockSerialPort,
            [self.available_port],
            )

    #{ Connection tests

    def test_connecting_to_existing_device(self):
        connection = self.factory.connect("/dev/pts/1")

        assert_is_instance(connection, SerialConnection)

        mock_port = connection._port
        eq_({"baudrate": 38400}, mock_port.init_kwargs)

    def test_connecting_with_specific_baud_rate(self):
        connection = self.factory.connect("/dev/pts/1", baudrate=1)

        mock_port = connection._port
        eq_({"baudrate": 1}, mock_port.init_kwargs)

    def test_connecting_with_port_extra_parameters(self):
        connection = self.factory.connect("/dev/pts/1", 1, "arg1", extra_arg=10)

        mock_port = connection._port
        eq_(("/dev/pts/1", "arg1"), mock_port.init_args)
        assert_dict_contains_subset({"extra_arg": 10}, mock_port.init_kwargs)

    def test_serial_port_error_when_connecting(self):
        port_class = _SerialPortCommunicationError
        factory = SerialConnectionFactory(port_class)
        connection = factory.connect("/dev/pts/1")
        eq_(None, connection)

    def test_connecting_to_non_existing_device(self):
        port_class = _SerialPortDeviceNotFoundError
        factory = SerialConnectionFactory(port_class)
        connection = factory.connect("/dev/madeup")
        eq_(None, connection)

    #{ Auto-connection tests

    def test_auto_connecting_with_existing_device(self):
        connection = self.factory.auto_connect()
        assert_is_instance(connection, SerialConnection)

    def test_auto_connecting_with_no_suitable_device_found(self):
        port_class = _SerialPortCommunicationError
        factory = SerialConnectionFactory(port_class)
        connection = factory.auto_connect()
        eq_(None, connection)

    def test_auto_connecting_with_specific_baud_rate(self):
        connection = self.factory.auto_connect(baudrate=1)

        mock_port = connection._port
        eq_({"baudrate": 1}, mock_port.init_kwargs)

    def test_auto_connecting_with_port_extra_parameters(self):
        connection = self.factory.auto_connect(1, "arg1", extra_arg=10)

        mock_port = connection._port
        eq_("arg1", mock_port.init_args[1])
        assert_dict_contains_subset({"extra_arg": 10}, mock_port.init_kwargs)


class TestSerialConnection(object):

    def setup(self):
        self.mock_port = _MockSerialPort()
        self.connection = SerialConnection(self.mock_port)

    def test_initialization(self):
        port = _MockSerialPort()
        connection = SerialConnection(port)

        eq_(port, connection._port)

    def test_closing(self):
        self.connection.close()

        assert_is_none(self.connection._port)
        self.mock_port._assert_method_was_called("close")


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
