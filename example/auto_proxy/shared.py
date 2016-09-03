from mqrpclib.rpc_exception import RpcException

class MyException(RpcException):
    def __init__(self, message=None):
        super(MyException, self).__init__(
            10,
            message or "Unknown Exception"
        )

