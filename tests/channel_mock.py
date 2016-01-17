class ChannelMock(object):
    def __init__(self, queues=None):
        self._queues = dict([(x, []) for x in queues or []])

    def queue_declare(self, queue=None, exclusive=False):
        pass

    def basic_consume(self, fn, queue):
        pass

    def basic_ack(self, delivery_tag):
        pass

    def basic_publish(
        self,
        exchange,
        routing_key,
        body,
        properties=None,
        mandatory=False,
        immediate=False
    ):
        if routing_key in self._queues:
            self._queues[routing_key].append(body)

    def mock_get_queue(self, routing_key):
        return self._queues.get(routing_key)

    def mock_clear_queue(self, routing_key=None):
        if routing_key:
            self._queues[routing_key] = []
        else:
            _keys = self._queues.keys()
            self._queues = dict([(x, []) for x in _keys])
