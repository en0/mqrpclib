from mqrpclib.rpc_exception import EX_CLIENT_TIMEOUT_EXCEPTION
from channel_mock import ChannelMock
from mqrpclib import RpcProxy
from mqrpclib.rpc_request_message import RpcRequestMessage
from mqrpclib.rpc_response_message import RpcResponseMessage
from prop_mock import PropMock
from time import sleep
from unittest import TestCase
from uuid import uuid4


class TestRpcServer(TestCase):
    def test_remote_exec_basic(self):
        __n = str(uuid4())
        __m = "test"
        __q = "{}.{}".format(__n, __m)

        _c = ChannelMock([__q])
        _p = RpcProxy(__n, _c)
        _p.remote_exec(__m, "v1", args={"a": 1}, blocking=False)
        _resp = RpcRequestMessage.loads(_c.mock_get_queue(__q)[0])
        self.assertEqual(_resp.version, "v1")
        self.assertDictEqual(_resp.args, {"a": 1})

    def test_remote_exec(self):
        __n = str(uuid4())
        __m = "test"
        __q = "{}.{}".format(__n, __m)

        _uuid = str(uuid4())
        _c, _p = None, None

        def _cb(corr_id):
            d = _c.mock_get_queue(__q)[0]
            _c.mock_clear_queue()
            _d = RpcRequestMessage.loads(d)
            _r = RpcResponseMessage(0, _d.args['a'])
            _m = None
            _pr = PropMock(reply_to=None, correlation_id=corr_id)
            _p._callback(_c, _m, _pr, _r.dumps())

        _c = ChannelMock([__q], _cb)
        _p = RpcProxy(__n, _c)
        resp = _p.remote_exec(__m, "v1", args={"a": _uuid})
        self.assertEqual(resp.return_value, _uuid)

    def test_remote_exec_timeout(self):
        __n = str(uuid4())
        __m = "test"
        __q = "{}.{}".format(__n, __m)

        _uuid = str(uuid4())
        _c, _p = None, None

        def _cb(corr_id):
            sleep(3)

        _c = ChannelMock([__q], _cb)
        _p = RpcProxy(__n, _c)
        resp = _p.remote_exec(__m, "v1", args={"a": _uuid}, timeout=2)
        self.assertEqual(resp.code, EX_CLIENT_TIMEOUT_EXCEPTION)

    def test_remote_exec_default_timeout(self):
        __n = str(uuid4())
        __m = "test"
        __q = "{}.{}".format(__n, __m)

        _uuid = str(uuid4())
        _c, _p = None, None

        def _cb(corr_id):
            sleep(3)

        _c = ChannelMock([__q], _cb)
        _p = RpcProxy(__n, _c, timeout=2)
        resp = _p.remote_exec(__m, "v1", args={"a": _uuid})
        self.assertEqual(resp.code, EX_CLIENT_TIMEOUT_EXCEPTION)
