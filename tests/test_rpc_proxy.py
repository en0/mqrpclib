from uuid import uuid4
from unittest import TestCase
from mqrpclib import RpcProxy
from mqrpclib.rpc_request_message import RpcRequestMessage
from mqrpclib.rpc_response_message import RpcResponseMessage
from channel_mock import ChannelMock
from prop_mock import PropMock


class TestRpcServer(TestCase):
    def test_remote_exec_basic(self):
        _c = ChannelMock(["test"])
        _p = RpcProxy(_c)
        _p.remote_exec("test", "v1", args={"a": 1}, blocking=False)
        self.assertEqual(
            _c.mock_get_queue("test")[0],
            '{"version": "v1", "args": {"a": 1}}'
        )

    def test_remote_exec(self):

        _uuid = str(uuid4())
        _c, _p = None, None

        def _cb(corr_id):
            d = _c.mock_get_queue("test")[0]
            _c.mock_clear_queue()
            _d = RpcRequestMessage.loads(d)
            _r = RpcResponseMessage(0, _d.args['a'])
            _m = None
            _pr = PropMock(reply_to=None, correlation_id=corr_id)
            _p._callback(_c, _m, _pr, _r.dumps())

        _c = ChannelMock(["test"], _cb)
        _p = RpcProxy(_c)
        resp = _p.remote_exec("test", "v1", args={"a": _uuid})
        self.assertEqual(resp.return_value, _uuid)
