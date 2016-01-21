LIBRARY_EXCEPTION = 0xF0000000
LIBRARY_EXCEPTION_CLIENT = 0x00F00000


# Service side exceptions
EX_UNHANDLED_EXCEPTION = LIBRARY_EXCEPTION
EX_REQUEST_EXCEPTION = LIBRARY_EXCEPTION + 1
EX_RESPONSE_EXCEPTION = LIBRARY_EXCEPTION + 2
EX_DISPATCH_EXCEPTION = LIBRARY_EXCEPTION + 3


class RpcException(Exception):
    def __init__(self, code, message=None):
        super(RpcException, self).__init__(message)
        self._code = code

    @property
    def code(self):
        return self._code


class UnhandledException(RpcException):
    def __init__(self, message=None):
        super(UnhandledException, self).__init__(
            EX_UNHANDLED_EXCEPTION,
            message or "Unknown Exception"
        )


class RequestException(RpcException):
    def __init__(self, message=None):
        super(RequestException, self).__init__(
            EX_REQUEST_EXCEPTION,
            message or "Request Exception"
        )


class ResponseException(RpcException):
    def __init__(self, message=None):
        super(ResponseException, self).__init__(
            EX_RESPONSE_EXCEPTION,
            message or "Response Exception"
        )


class DispatchException(RpcException):
    def __init__(self, message=None):
        super(DispatchException, self).__init__(
            EX_DISPATCH_EXCEPTION,
            message or "Dispatch Exception"
        )


# Client side exceptions
EX_CLIENT_TIMEOUT_EXCEPTION = LIBRARY_EXCEPTION_CLIENT + 1


class ProxyTimeoutException(RpcException):
    def __init__(self, message=None):
        super(ProxyTimeoutException, self).__init__(
            EX_CLIENT_TIMEOUT_EXCEPTION,
            message or "Proxy Timeout Exception"
        )


_exception_map = {
    EX_UNHANDLED_EXCEPTION: UnhandledException,
    EX_REQUEST_EXCEPTION: RequestException,
    EX_RESPONSE_EXCEPTION: ResponseException,
    EX_DISPATCH_EXCEPTION: DispatchException,
    EX_CLIENT_TIMEOUT_EXCEPTION: ProxyTimeoutException,
}


def get_exception_by_code(code, extended_codes=None):
    """ Get the exception class for the given code.

    Retrieve the class of an exception given a specific exception code. This is
    useful if you have a client proxy that re-raises exceptions generated on
    the server.

    Arguments:
        code:
            The RpcResponseMessage code given in response to a failed request.
        extended_codes:
            Optional, extend the exception lookup map with additional exception
            classes. This is useful if a service provides specific return codes.

    Returns: class or None
    """
    _map = _exception_map.copy()

    if extended_codes:
        _map.update(extended_codes)

    if code in _map:
        return _map[code]

    return None


def get_return_or_raise_exception(response_message, extended_codes=None):
    """ Return the return_value or re-raise server exception.

    If the response has a non-zero code, the corresponding server exception
    will be raised if it can be identified. If it cannot be identified, a
    generic RpcException will be raised.

    If the response has a zero code, the return_value will be returned.

    Arguments:

        response_message:
            The RpcResponseMessage to explore.

        extended_codes:
            Optional, extend the exception lookup map with additional exception
            classes. This is useful if a service provides specific return codes.

    Returns:
        The return value of the response.

    Raises:
        If code is non-zero, A RpcException corresponding to the code in the
        message.
    """

    if response_message:
        return response_message.return_value

    _extype = get_exception_by_code(response_message.code, extended_codes)

    if _extype:
        _exception = _extype(response_message.error_message)
    else:
        _exception = RpcException(
            response_message.code,
            response_message.error_message
        )

    raise _exception
