import json
import rpc_exception as exp


class RpcRequestMessage(object):
    @classmethod
    def loads(cls, raw_data):
        try:
            data = json.loads(raw_data)
            return cls(data.get("version"), data.get("args"))

        except ValueError as ex:
            raise exp.RequestException(
                "Unable to deserialize request: {}".format(ex.message)
            )

    @property
    def version(self):
        return self._version

    @property
    def args(self):
        return self._args

    def dumps(self):
        return json.dumps({
            "version": self._version,
            "args": self._args
        })

    def __init__(self, version, args):
        self._version = version
        self._args = args

    def __repr__(self):
        return "<RequestMessage(version='{}', args='{}')".format(
            self.version,
            self.args
        )
