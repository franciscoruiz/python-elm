from uuid import uuid4

from nose.tools import assert_in
from nose.tools import eq_


def _mock_method(function):
    function_name = function.func_name
    def decorator(self, *args, **kwargs):
        self._method_calls[function_name] = (args, kwargs)
        result = function(self, *args, **kwargs)
        return result
    return decorator


class MockSerialPort(object):

    def __init__(self):
        self._method_calls = {}
        self._data_written = []
        self._data_read = []

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

    def assert_data_was_written(self, data):
        assert_in(
            data,
            self._data_written,
            "Data {!r} was not written to the port".format(data),
            )

    def assert_data_was_read(self, data):
        assert_in(
            data,
            self._data_read,
            "Data {!r} was not read from the port".format(data),
            )

    @_mock_method
    def read(self):
        response = _generate_random_response()
        self._data_read.append(response)
        return response

    @_mock_method
    def write(self, data):
        self._data_written.append(data)

    @_mock_method
    def flushOutput(self):
        pass

    @_mock_method
    def flushInput(self):
        pass

    @_mock_method
    def close(self):
        pass


def _generate_random_response():
    return uuid4().hex
