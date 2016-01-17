from unittest import TestCase
from mqrpclib import RpcServer
from channel_mock import ChannelMock
from uuid import uuid4


class TestRpcServer(TestCase):
    def test_register(self):
        _uuid = uuid4()
        _s = RpcServer(ChannelMock())
        _s.register('apple', 'sauce', _uuid)
        self.assertEqual(
            _s._get_function('apple', 'sauce'),
            _uuid
        )

    def test_register_multi(self):
        _uuid1 = uuid4()
        _uuid2 = uuid4()
        _s = RpcServer(ChannelMock())
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
        _s = RpcServer(ChannelMock())
        _s.register('apple', 'sauce', _uuid1)
        self.assertRaises(
            Exception,
            _s.register,
            'apple', 'sauce', _uuid2
        )

    def test_service_description(self):
        _s = RpcServer(ChannelMock())
        _uuid = uuid4()
        _s.service_description = _uuid
        self.assertEqual(_s.service_description, _uuid)

    def test_service_description_via_help(self):
        _s = RpcServer(ChannelMock())
        _uuid = uuid4()
        _s.service_description = _uuid
        self.assertEqual(_s._help()['service'], _uuid)
