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
        conn = pika.BlockingConnection(pika.URLParameters(url))
        chan = conn.channel()
        _proxy = cls(chan, timeout)

        try:
            yield _proxy
        finally:
            conn.close()

    def remote_exec(self, name, version, args, blocking=True):
        _req = RpcRequestMessage(version, args)
        _corr_id = str(uuid4())
        self._response[_corr_id] = None

        self._chan.basic_publish(
            exchange='',
            routing_key=name,
            properties=pika.BasicProperties(
                correlation_id=_corr_id,
                reply_to=self._callback_queue
            ),
            body=_req.dumps()
        )

        # If not blocking, return the correlation id so the caller can lookup
        # the return if it wants too.
        if not blocking:
            return _corr_id

        return self.get_response(_corr_id, clear_response=True, wait=True)

    def has_response(self, correlation_id):
        # TODO: This is streaching the Law of Demeter just a little bit.
        # Are there other options?
        self._chan.connection.process_data_events()
        return (self._response[correlation_id] is not None)

    def get_response(self, correlation_id, clear_response=True, wait=False):
        while wait and not self.has_response(correlation_id):
            pass

        _resp = RpcResponseMessage.loads(self._response[correlation_id])

        if clear_response:
            del self._response[correlation_id]

        return _resp

    def __init__(self, chan, timeout=None):
        self._logger = logging.getLogger(__name__)
        self._response = {}
        self._timeout = timeout or 30
        self._chan = chan
        self._callback_queue = self._chan.queue_declare(
            exclusive=True
        ).method.queue
        self._chan.basic_consume(
            self._callback,
            self._callback_queue,
            no_ack=True
        )

    def _callback(self, ch, meth, prop, body):
        if prop.correlation_id in self._response:
            self._response[prop.correlation_id] = body
