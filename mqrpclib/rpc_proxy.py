from rpc_request_message import RpcRequestMessage
from rpc_response_message import RpcResponseMessage
from uuid import uuid4
from contextlib import contextmanager
import logging
import pika


class RpcProxy(object):
    @classmethod
    @contextmanager
    def context(cls, url, timeout=None):
        _proxy = cls(url, timeout)
        try:
            _proxy.connect()
            yield _proxy
        finally:
            _proxy.disconnect()

    def connect(self):
        if self.is_connected:
            return

        _conn = pika.BlockingConnection(self._parameters)
        _chan = _conn.channel()
        _respq = _chan.queue_declare(exclusive=True)
        _callback_queue = _respq.method.queue
        _chan.basic_consume(self._callback, _callback_queue, no_ack=True)

        self._rabbit = {
            "conn": _conn,
            "chan": _chan,
            "callback_queue": _callback_queue
        }

    def disconnect(self):
        if self.is_connected:
            self._rabbit['conn'].close()

        self._rabbit = None

    def remote_exec(self, name, version, args, blocking=True):
        _req = RpcRequestMessage(version, args)
        _corr_id = str(uuid4())
        self._response[_corr_id] = None

        self._rabbit['chan'].basic_publish(
            exchange='',
            routing_key=name,
            properties=pika.BasicProperties(
                correlation_id=_corr_id,
                reply_to=self._rabbit['callback_queue']
            ),
            body=_req.dumps()
        )

        # If not blocking, return the correlation id so the caller can lookup
        # the return if it wants too.
        if not blocking:
            return _corr_id

        return self.get_response(_corr_id, clear_response=True, wait=True)

    def has_response(self, correlation_id):
        self._rabbit['conn'].process_data_events()
        return (self._response[correlation_id] is not None)

    def get_response(self, correlation_id, clear_response=True, wait=False):
        while wait and not self.has_response(correlation_id):
            pass

        _resp = RpcResponseMessage.loads(self._response[correlation_id])

        if clear_response:
            del self._response[correlation_id]

        return _resp

    @property
    def is_connected(self):
        if self._rabbit and 'conn' in self._rabbit:
            return self._rabbit['conn'].is_open
        return False

    def __init__(self, url, timeout=None):
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout or 30
        self._parameters = pika.URLParameters(url)
        self._rabbit = None
        self._response = {}

    def _callback(self, ch, meth, prop, body):
        if prop.correlation_id in self._response:
            self._response[prop.correlation_id] = body
