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

_OBD_RESPONSE_NO_DATA = "NO DATA"

_OBD_RESPONSE_UNSUPPORTED_COMMAND = "?"

_INT_TO_HEX_WORD_FORMATTER = "{:0=2X}"

_INT_TO_HEX_WORD_FORMATTER_PRETTY = "{:0=#4x}"


class ELMError(Exception):

    pass


class CommandNotSupportedError(ELMError):

    pass


class OBDCommand(object):

    def __init__(self, mode, pid):
        self.mode = mode
        self.pid = pid

    def to_hex_words(self, pretty=False):
        hex_words = (
            _convert_int_to_hex_word(self.mode, pretty=pretty),
            _convert_int_to_hex_word(self.pid, pretty=pretty),
            )
        return hex_words

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash((self.mode, self.pid))

    def __repr__(self):
        return "{}(mode={}, pid={})".format(
            self.__class__.__name__,
            *self.to_hex_words(True)
            )


def _convert_int_to_hex_word(i, pretty=False):
    if pretty:
        formatter = _INT_TO_HEX_WORD_FORMATTER_PRETTY
    else:
        formatter = _INT_TO_HEX_WORD_FORMATTER

    return formatter.format(i)


class OBDResponse(object):

    def __init__(self, raw_data):
        self.raw_data = raw_data


def make_obd_response(response_raw):
    if response_raw == _OBD_RESPONSE_NO_DATA:
        return None

    if response_raw == _OBD_RESPONSE_UNSUPPORTED_COMMAND:
        raise CommandNotSupportedError()

    response_words = _convert_raw_response_to_words(response_raw)
    raw_data = tuple(response_words[2:])
    return OBDResponse(raw_data)


def _convert_raw_response_to_words(raw_response):
    words_as_str = raw_response.split()
    words = [int(word, 16) for word in words_as_str]
    return words
