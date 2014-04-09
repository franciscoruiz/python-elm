from unittest import skip

from nose.tools import assert_false
from nose.tools import assert_raises
from nose.tools import eq_
from nose.tools import ok_

from elm327.obd import NoDataReceivedError
from elm327.obd import OBDCommand
from elm327.obd import OBDResponse
from elm327.obd import UnsupportedCommandError


_OBD_COMMAND = OBDCommand(0x01, 0x10)


class TestOBDCommand(object):

    def test_conversion_to_hex_words(self):
        hex_words = _OBD_COMMAND.to_hex_words()
        eq_(("01", "10"), hex_words)

    def test_conversion_to_pretty_hex_words(self):
        hex_words = _OBD_COMMAND.to_hex_words(True)
        eq_(("0x01", "0x10"), hex_words)

    def test_repr(self):
        eq_('OBDCommand(mode=0x01, pid=0x10)', repr(_OBD_COMMAND))


class TestOBDResponseConstruction(object):

    def test_requested_command_identification(self):
        """
        The command the resulted in the response can be identified from the
        response.

        """
        response = OBDResponse.make("41 10 00 00 00")
        eq_(_OBD_COMMAND, response.command)

    def test_response_raw_data(self):
        response = OBDResponse.make("41 10 0A 0B 0C D0")
        expected_raw_data = (10, 11, 12, 208)
        eq_(expected_raw_data, response.raw_data)

    def test_no_data_received(self):
        """
        An exception is raised when a "NO DATA" response is received.

        """
        with assert_raises(NoDataReceivedError):
            OBDResponse.make("NO DATA")

    def test_unsupported_command_response(self):
        """
        An exception is raised when a "?" response is received.

        """
        with assert_raises(UnsupportedCommandError):
            OBDResponse.make("?")
