import rpc_exception as exp
import json


class RpcResponseMessage(object):
    @classmethod
    def loads(cls, raw_data):
        data = json.loads(raw_data)
        return cls(
            data["code"],
            data["return_value"],
            data["error_message"]
        )

    def __bool__(self):
        return self.code == 0

    def __nonzero__(self):
        return self.__bool__()

    @property
    def code(self):
        return self._code

    @property
    def return_value(self):
        return self._return_value

    @property
    def error_message(self):
        return self._error_message

    def dumps(self):
        try:
            return json.dumps({
                "code": self._code,
                "return_value": self._return_value,
                "error_message": self._error_message
            })
        except ValueError as ex:
            raise exp.ResponseException(
                "Unable to serialize response: {}".format(ex.message)
            )

    def __init__(self, code, return_value=None, error_message=None):
        self._code = code
        self._return_value = return_value
        self._error_message = error_message

    def __repr__(self):
        return "".join([
            "<ResponseMessage(",
            "code='{}', ",
            "return_value='{}', ",
            "error_message='{}')"
        ]).format(
            self.code,
            self.return_value,
            self.error_message
        )
