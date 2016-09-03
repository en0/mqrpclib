from unittest import TestCase
from mqrpclib import RpcServer
from channel_mock import ChannelMock
from method_mock import MethodMock
from prop_mock import PropMock
from uuid import uuid4
from mqrpclib.rpc_request_message import RpcRequestMessage
from mqrpclib.rpc_response_message import RpcResponseMessage


class TestRpcServer(TestCase):
    def test_register(self):
        _uuid = uuid4()
        _s = RpcServer("green", ChannelMock())
        _s.register('apple', 'sauce', _uuid)
        self.assertEqual(
            _s._get_function('apple', 'sauce'),
            _uuid
        )

    def test_register_multi(self):
        _uuid1 = uuid4()
        _uuid2 = uuid4()
        _s = RpcServer("green", ChannelMock())
        _s.register('apple', 'sauce', _uuid1)
        _s.register('apple', 'juice', _uuid2)
        self.assertEqual(
            _s._get_function('apple', 'sauce'),
            _uuid1
        )
        self.assertEqual(
            _s._get_function('apple', 'juice'),
            _uuid2
        )

    def test_register_duplicate_version(self):
        _uuid1 = uuid4()
        _uuid2 = uuid4()
        _s = RpcServer("green", ChannelMock())
        _s.register('apple', 'sauce', _uuid1)
        self.assertRaises(
            Exception,
            _s.register,
            'apple', 'sauce', _uuid2
        )

    def test_service_name(self):
        _uuid = str(uuid4())
        _s = RpcServer(_uuid, ChannelMock())
        self.assertEqual(_s.service_name, _uuid)
    
    def test_service_name_via_help(self):
        _uuid = str(uuid4())
        _s = RpcServer(_uuid, ChannelMock())
        print _s._help()
        self.assertEqual(_s._help()['service'], _uuid)

    def test_service_description(self):
        _s = RpcServer("green", ChannelMock())
        _uuid = uuid4()
        _s.service_description = _uuid
        self.assertEqual(_s.service_description, _uuid)

    def test_service_description_via_help(self):
        _s = RpcServer("green", ChannelMock())
        _uuid = uuid4()
        _s.service_description = _uuid
        self.assertEqual(_s._help()['description'], _uuid)

    def test_request_handler(self):
        print ("thisone")
        a, b, c = 1, 2, 3

        def dummy_method(a, b):
            return a + b

        _corr_id = uuid4()
        _reply_to = str(uuid4())

        _c = ChannelMock([_reply_to])
        _m = MethodMock(routing_key="green.dummy_method")
        _p = PropMock(_reply_to, str(_corr_id))

        _req = RpcRequestMessage("v1", None, dict(a=a, b=b))

        _c.mock_clear_queue(_reply_to)

        _s = RpcServer("green", _c)
        _s.register("dummy_method", "v1", dummy_method)
        _s._request_handler(_c, _m, _p, _req.dumps())

        _resp = RpcResponseMessage.loads(_c.mock_get_queue(_reply_to)[0])
        self.assertEqual(_resp.return_value, c)

    def test_request_handler_noversion(self):
        def dummy_method(a, b):
            return a + b

        _corr_id = uuid4()
        _reply_to = str(uuid4())

        _c = ChannelMock([_reply_to])
        _m = MethodMock(routing_key="green.dummy_method")
        _p = PropMock(_reply_to, str(_corr_id))

        _req = RpcRequestMessage("v2", None, dict(a=None, b=None))

        _c.mock_clear_queue(_reply_to)

        _s = RpcServer("green", _c)
        _s.register("dummy_method", "v1", dummy_method)
        _s._request_handler(_c, _m, _p, _req.dumps())

        _resp = RpcResponseMessage.loads(_c.mock_get_queue(_reply_to)[0])
        self.assertEqual(_resp.code, 0xf0000003)

    def test_request_handler_bad_request_format(self):
        _corr_id = uuid4()
        _reply_to = str(uuid4())

        _c = ChannelMock([_reply_to])
        _m = MethodMock(routing_key="green.")
        _p = PropMock(_reply_to, str(_corr_id))

        _c.mock_clear_queue(_reply_to)

        _s = RpcServer("green", _c)
        _s._request_handler(_c, _m, _p, "}")

        _resp = RpcResponseMessage.loads(_c.mock_get_queue(_reply_to)[0])
        self.assertEqual(_resp.code, 0xf0000001)

    def test_request_handler_unhandled_exception(self):
        a, b = 1, 'a'

        def dummy_method(a, b):
            return a + b

        _corr_id = uuid4()
        _reply_to = str(uuid4())

        _c = ChannelMock([_reply_to])
        _m = MethodMock(routing_key="green.dummy_method")
        _p = PropMock(_reply_to, str(_corr_id))

        _req = RpcRequestMessage("v1", None, dict(a=a, b=b))

        _c.mock_clear_queue(_reply_to)

        _s = RpcServer("green", _c)
        _s.register("dummy_method", "v1", dummy_method)
        _s._request_handler(_c, _m, _p, _req.dumps())

        _resp = RpcResponseMessage.loads(_c.mock_get_queue(_reply_to)[0])
        self.assertEqual(_resp.code, 0xf0000000)
