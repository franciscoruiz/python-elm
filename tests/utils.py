from itertools import islice

from nose.tools import assert_in
from nose.tools import eq_
from nose.tools import ok_


def _mock_method(function):
    function_name = function.func_name
    def decorator(self, *args, **kwargs):
        self._method_calls.append((function_name, args, kwargs))
        result = function(self, *args, **kwargs)
        return result
    return decorator


class MockSerialPort(object):

    def __init__(self, writer=None, reader=None):
        self._method_calls = []

        self._data_writer = writer or MockSerialPortDataWriter()

        self._data_reader = reader or MockSerialPortDataReader()

    def assert_method_was_called(self, method_name, *args, **kwargs):
        method_calls = \
            [call[1:] for call in self._method_calls if call[0] == method_name]

        ok_(
            method_calls,
            "Method {!r} was not called".format(method_name),
            )

        wrong_arguments_message = \
            "Method {!r} was not called with the expected arguments: " \
            "Expected: {}".format(
                method_name,
                (args, kwargs),
                )
        assert_in(
            (args, kwargs),
            method_calls,
            wrong_arguments_message,
            )

    def assert_data_was_written(self, expected_data):
        if not expected_data.endswith("\n\r"):
            expected_data += "\n\r"

        actual_data = self._data_writer.data_written
        eq_(
            expected_data,
            actual_data,
            "Data {!r} was not written to the port, found {!r}".format(
                expected_data,
                actual_data,
                ),
            )

    def assert_data_was_read(self, data):
        if not data.endswith(">"):
            data += ">"

        eq_(
            data,
            self._data_reader.data_read,
            "Data {!r} was not read from the port".format(data),
            )

    def assert_scenario(self, *calls):
        for expected_call, actual_call in zip(calls, self._method_calls):
            expected_method_name, expected_args, expected_kwargs = expected_call
            actual_method_name, actual_args, actual_kwargs = actual_call

            eq_(
                expected_method_name,
                actual_method_name,
                "Expected call to {!r} found {!r}".format(
                    expected_method_name,
                    actual_method_name,
                    )
                )
            eq_(
                expected_args,
                actual_args,
                "In call to {!r} expected args {!r} found {!r}".format(
                    expected_method_name,
                    expected_args,
                    actual_args,
                    )
                )
            eq_(
                expected_args,
                actual_args,
                "In call to {!r} expected kwargs {!r} found {!r}".format(
                    expected_method_name,
                    expected_kwargs,
                    actual_kwargs,
                    )
                )

    @_mock_method
    def read(self, size=1):
        return self._data_reader.read(size)

    @_mock_method
    def write(self, data):
        self._data_writer.write(data)

    @_mock_method
    def flushOutput(self):
        pass

    @_mock_method
    def flushInput(self):
        pass

    @_mock_method
    def close(self):
        pass


class MockSerialPortDataWriter(object):

    def __init__(self):
        self.data_written = ""

    def write(self, data):
        self.data_written += data


class MockSerialPortDataReader(object):

    def __init__(self, data=None):
        data = data or "constant response"
        if ">" not in data:
            data += ">"
        self._expected_data = iter(data)

        self.data_read = ""

    def read(self, size):
        chunk = "".join(islice(self._expected_data, size))
        self.data_read += chunk
        return chunk
