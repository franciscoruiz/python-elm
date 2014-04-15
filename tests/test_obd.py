from nose.tools import assert_false
from nose.tools import assert_is_none
from nose.tools import assert_raises
from nose.tools import eq_
from nose.tools import ok_

from elm327.obd import CommandNotSupportedError
from elm327.obd import OBDCommand
from elm327.obd import make_obd_response


_OBD_COMMAND = OBDCommand(0x01, 0x10)


class TestOBDCommand(object):

    def test_conversion_to_hex_words(self):
        hex_words = _OBD_COMMAND.to_hex_words()
        eq_(("01", "10"), hex_words)

    def test_conversion_to_pretty_hex_words(self):
        hex_words = _OBD_COMMAND.to_hex_words(True)
        eq_(("0x01", "0x10"), hex_words)

    def test_repr(self):
        eq_("OBDCommand(mode=0x01, pid=0x10)", repr(_OBD_COMMAND))

    def test_equality(self):
        ok_(_OBD_COMMAND == _OBD_COMMAND)
        ok_(_OBD_COMMAND == OBDCommand(_OBD_COMMAND.mode, _OBD_COMMAND.pid))

        assert_false(_OBD_COMMAND == OBDCommand(_OBD_COMMAND.mode, 0xAA))
        assert_false(_OBD_COMMAND == OBDCommand(0xAA, _OBD_COMMAND.pid))

        assert_false(_OBD_COMMAND == None)

    def test_hash(self):
        eq_(hash(_OBD_COMMAND), hash(_OBD_COMMAND))


class TestOBDResponseConstruction(object):

    def test_response_raw_data(self):
        response = make_obd_response("41 10 0A 0B 0C D0")
        expected_raw_data = (10, 11, 12, 208)
        eq_(expected_raw_data, response.raw_data)

    def test_no_data_received(self):
        """
        An exception is raised when a "NO DATA" response is received.

        """
        response = make_obd_response("NO DATA")
        assert_is_none(response)

    def test_unsupported_command_response(self):
        """
        An exception is raised when a "?" response is received.

        """
        with assert_raises(CommandNotSupportedError):
            make_obd_response("?")
