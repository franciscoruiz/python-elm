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
import time

from serial import Serial
from serial.serialutil import SerialException
from serial.tools.list_ports import comports

from elm327.obd import CommandNotSupportedError
from elm327.obd import OBDCommand
from elm327.obd import make_obd_response


class ConnectionError(Exception):

    pass


class SerialConnection(object):

    _LOGGER = getLogger(__name__ + "SerialConnection")

    def __init__(self, port):
        self._port = port

    def send_command(self, data, read_delay=None):
        """Write "data" to the port and return the response form it"""
        self._write(data)
        if read_delay:
            time.sleep(read_delay)
        return self._read()

    def close(self):
        self._port.close()
        self._port = None

    def _write(self, data):
        self._port.flushInput()
        self._port.flushOutput()
        self._port.write(data)
        self._port.write("\n\r")

    def _read(self):
        response = ""
        while True:
            c = self._port.read(1)
            if not c or c == ">":
                break
            if c == "\x00":
                continue
            response += c

        return response


class SerialConnectionFactory(object):

    _DEFAULT_BAUDRATE = 38400

    _LOGGER = getLogger(__name__ + "SerialConnectionFactory")

    def __init__(
        self,
        connection_class=SerialConnection,
        port_class=Serial,
        available_ports=None,
        ):
        self._connection_class = connection_class
        self._port_class = port_class
        self._available_ports = available_ports

    def auto_connect(self, *args, **kwargs):
        connection = None
        for device_name in self._get_available_ports():
            try:
                port = self._open_port(device_name, *args, **kwargs)
            except ConnectionError:
                self._LOGGER.debug("Failed to connect to %r", device_name)
                continue
            else:
                self._LOGGER.info("Connected to %r", device_name)
                connection = self._connection_class(port)
                break
        return connection

    def connect(self, device_name, *args, **kwargs):
        port = self._open_port(device_name, *args, **kwargs)
        self._LOGGER.info("Connected to %r", device_name)
        connection = self._connection_class(port)
        return connection

    def _open_port(self, device_name, baudrate=_DEFAULT_BAUDRATE, *args, **kwargs):
        try:
            port = self._port_class(
                device_name,
                baudrate=baudrate,
                *args,
                **kwargs
                )
        except (SerialException, OSError) as exc:
            raise ConnectionError(str(exc))
        return port

    def _get_available_ports(self):
        if not self._available_ports:
            ports = comports()
            self._available_ports = [port[0] for port in ports]

        return self._available_ports


class ELMInterfaceConnection(SerialConnection):

    _UNSUPPORTED_PID_COMMANDS = [
        OBDCommand(0x01, 0x01),
        OBDCommand(0x01, 0x21),
        OBDCommand(0x01, 0x41),
        OBDCommand(0x01, 0x61),
        OBDCommand(0x01, 0x81),
        OBDCommand(0x01, 0xA1),
        OBDCommand(0x01, 0xC1),
        ]

    _LOGGER = getLogger(__name__ + "ELMInterfaceConnection")

    def __init__(self, *args, **kwargs):
        super(ELMInterfaceConnection, self).__init__(*args, **kwargs)

        self._unsupported_commands = []

        self.send_command("AT Z")
        self.send_command("AT E0")

    def send_command(self, data, read_delay=None):
        super_ = super(ELMInterfaceConnection, self)
        response = super_.send_command(data, read_delay)
        return response.strip()

    def send_obd_command(self, command, read_delay=None):
        if command in self._unsupported_commands:
            raise CommandNotSupportedError()

        command_data = ' '.join(command.to_hex_words())
        response_data = self.send_command(command_data, read_delay)

        try:
            response = make_obd_response(response_data)
        except CommandNotSupportedError:
            self._unsupported_commands.append(command)
            raise

        return response
