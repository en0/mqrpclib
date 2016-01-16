LIBRARY_EXCEPTION_MASK = 0xF0000000


class ExceptionBase(Exception):
    def __init__(self, code, message=None):
        super(ExceptionBase, self).__init__(message)
        self._code = code

    @property
    def code(self):
        return self._code


class UnhandledException(ExceptionBase):
    def __init__(self, message=None):
        super(UnhandledException, self).__init__(
            LIBRARY_EXCEPTION_MASK,
            message or "Unknown Exception"
        )


class RequestException(ExceptionBase):
    def __init__(self, message=None):
        super(RequestException, self).__init__(
            LIBRARY_EXCEPTION_MASK | 1,
            message or "Request Exception"
        )


class ResponseException(ExceptionBase):
    def __init__(self, message=None):
        super(ResponseException, self).__init__(
            LIBRARY_EXCEPTION_MASK | 2,
            message or "Response Exception"
        )


class DispatchException(ExceptionBase):
    def __init__(self, message=None):
        super(DispatchException, self).__init__(
            LIBRARY_EXCEPTION_MASK | 3,
            message or "Dispatch Exception"
        )
