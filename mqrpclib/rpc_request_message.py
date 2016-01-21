from version import VERSION
import json
import rpc_exception as exp


class RpcRequestMessage(object):
    @classmethod
    def loads(cls, raw_data):
        try:
            data = json.loads(raw_data)
            return cls(
                data.get("version"),
                data.get("args"),
                data["_mqrpclib_version"],
            )

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
            "args": self._args,
            "_mqrpclib_version": self._mqrpclib_version,
        })

    def __init__(self, version, args, mqrpclib_version=None):
        self._version = version
        self._args = args
        self._mqrpclib_version = mqrpclib_version or VERSION

    def __repr__(self):
        return "<RequestMessage(version='{}', args='{}')".format(
            self.version,
            self.args
        )
