from nose.tools import assert_dict_contains_subset
from nose.tools import assert_is_instance
from nose.tools import eq_
from serial.serialutil import SerialException

from elm327.connection import SerialConnection
from elm327.connection import SerialConnectionFactory


class TestSerialConnectionFactory(object):

    def setup(self):
        self.available_port = ('/dev/pts/1', 'pts1', 'HardCodedPort')
        self.factory = SerialConnectionFactory(
            _InitializableMockSerialPort,
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


class _SerialPortWithErrorOnInit(object):

    _EXCEPTION_CLASS = SerialException

    def __init__(self, *args, **kwargs):
        raise self._EXCEPTION_CLASS()


class _SerialPortCommunicationError(_SerialPortWithErrorOnInit):

    _EXCEPTION_CLASS = SerialException


class _SerialPortDeviceNotFoundError(_SerialPortWithErrorOnInit):

    _EXCEPTION_CLASS = OSError


class _InitializableMockSerialPort(object):

    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs
