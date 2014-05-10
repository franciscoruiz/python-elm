from nose.tools import assert_dict_contains_subset
from nose.tools import assert_in
from nose.tools import assert_is_instance
from nose.tools import assert_is_none
from nose.tools import assert_raises
from nose.tools import eq_
from serial.serialutil import SerialException
from serial.tools.list_ports import comports

from elm327.connection import ConnectionError
from elm327.connection import SerialConnection
from elm327.connection import SerialConnectionFactory


class TestSerialConnectionFactory(object):

    # { Connection tests

    def test_connecting_to_existing_device(self):
        factory = SerialConnectionFactory(port_class=_InitializableMockSerialPort)
        connection = factory.connect("/dev/pts/1")

        assert_is_instance(connection, SerialConnection)

    def test_connecting_with_specific_baud_rate(self):
        factory = SerialConnectionFactory(
            port_class=_InitializableMockSerialPort,
            baudrate=1,
            )
        connection = factory.connect("/dev/pts/1")

        mock_port = connection._port
        eq_({"baudrate": 1}, mock_port.init_kwargs)

    def test_connecting_with_port_extra_parameters(self):
        factory = SerialConnectionFactory(
            port_class=_InitializableMockSerialPort,
            extra_arg=10,
            )
        connection = factory.connect("/dev/pts/1")

        mock_port = connection._port
        eq_({"baudrate": 38400, "extra_arg": 10}, mock_port.init_kwargs)

    def test_serial_port_error_when_connecting(self):
        port_class = _SerialPortCommunicationError
        factory = SerialConnectionFactory(port_class)
        with assert_raises(ConnectionError):
            factory.connect("/dev/pts/1")

    def test_connecting_to_non_existing_device(self):
        port_class = _SerialPortDeviceNotFoundError
        factory = SerialConnectionFactory(port_class)
        with assert_raises(ConnectionError):
            factory.connect("/dev/madeup")

    # { Auto-connection tests

    def test_auto_connecting_with_existing_device(self):
        factory = SerialConnectionFactory(port_class=_InitializableMockSerialPort)

        connection = factory.auto_connect(["/dev/pts/1"])

        assert_is_instance(connection, SerialConnection)
        eq_("/dev/pts/1", connection._port.init_args[0])

    def test_auto_connecting_with_default_ports(self):
        """
        The system is scanned to check for available ports if an explicit
        list is not provided

        """
        factory = SerialConnectionFactory(
            port_class=_InitializableMockSerialPort,
            )
        connection = factory.auto_connect()

        device_names = [port[0] for port in comports()]
        if device_names:
            assert_in(connection._port.init_args[0], device_names)
        else:
            assert_is_none(connection)

    def test_auto_connecting_with_no_suitable_device_found(self):
        port_class = _SerialPortCommunicationError
        factory = SerialConnectionFactory(port_class)

        connection = factory.auto_connect(["/dev/pts/1"])

        eq_(None, connection)

    def test_auto_connecting_with_specific_baud_rate(self):
        factory = SerialConnectionFactory(
            port_class=_InitializableMockSerialPort,
            baudrate=1,
            )

        connection = factory.auto_connect(["/dev/pts/1"])

        mock_port = connection._port
        eq_({"baudrate": 1}, mock_port.init_kwargs)

    def test_auto_connecting_with_port_extra_parameters(self):
        factory = SerialConnectionFactory(
            _InitializableMockSerialPort,
            extra_arg=10,
            )

        connection = factory.auto_connect(["/dev/pts/1"])

        mock_port = connection._port
        eq_({"baudrate": 38400, "extra_arg": 10}, mock_port.init_kwargs)


class _SerialPortWithErrorOnInit(object):

    _EXCEPTION_CLASS = SerialException

    def __init__(self, *args, **kwargs):
        raise self._EXCEPTION_CLASS()


class _SerialPortCommunicationError(_SerialPortWithErrorOnInit):

    _EXCEPTION_CLASS = SerialException


class _SerialPortDeviceNotFoundError(_SerialPortWithErrorOnInit):

    _EXCEPTION_CLASS = OSError


class _MockSerialConnection(object):

    def __init__(self, *args, **kwargs):
        pass


class _InitializableMockSerialPort(object):

    def __init__(self, *args, **kwargs):
        self.init_args = args
        self.init_kwargs = kwargs
