from datetime import datetime

from nose.tools import assert_is_none
from nose.tools import eq_

from elm327.connection import SerialConnection
from tests.utils import MockSerialPort


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
        self.mock_port._assert_method_was_called("close")


class _MockSerialPortWithTimings(MockSerialPort):

    def __init__(self, *args, **kwargs):
        super(_MockSerialPortWithTimings, self).__init__(*args, **kwargs)

        self._last_read_time = None
        self._last_write_time = None

    def read(self):
        self._last_read_time = datetime.now()

    def write(self, data):
        super(_MockSerialPortWithTimings, self).write(data)
        self._last_write_time = datetime.now()


class _MockSerialPortWithConstantResponse(MockSerialPort):

    def __init__(self, response, *args, **kwargs):
        super(_MockSerialPortWithTimings, self).__init__(*args, **kwargs)

        self._response = response

    def read(self):
        return MockSerialPort.read(self)
