################################################################################
# The MIT License (MIT)
#
# Copyright (c) 2014 Francisco Ruiz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################

from logging import getLogger

from serial import Serial
from serial.serialutil import SerialException
from serial.tools.list_ports import comports


class SerialConnection(object):

    _PORT_CLASS = Serial

    _DEFAULT_BAUDRATE = 38400

    _LOGGER = getLogger(__name__ + 'SerialConnection')

    def __init__(self, port):
        self._port = port

    @classmethod
    def auto_connect(cls, *args, **kwargs):
        connection = None
        for device_name, device_description, hardware_id in comports():
            device_description = "{} ({} - ID: {})".format(
                device_description,
                device_name,
                hardware_id,
                )
            cls._LOGGER.debug('Trying to connect to %s', device_description)
            connection = cls.connect(device_name, *args, **kwargs)
            if connection:
                cls._LOGGER.info('Connected to %s', device_description)
                break
        return connection

    @classmethod
    def connect(cls, device_name, baudrate=_DEFAULT_BAUDRATE, *args, **kwargs):
        try:
            port = \
                cls._PORT_CLASS(device_name, baudrate=baudrate, *args, **kwargs)
        except (SerialException, OSError):
            cls._LOGGER.exception('Could not connect to device %r', device_name)
            connection = None
        else:
            connection = cls(port)

        return connection

    def close(self):
        self._port.close()
        self._port = None
