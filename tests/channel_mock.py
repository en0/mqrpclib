from method_mock import MethodMock


class ChannelMock(object):
    def __init__(self, queues=None, process_data_events_callback=None):
        self._queues = dict([(x, []) for x in queues or []])
        self._corr_id = None
        self._funcs = {}
        self._process_data_events_callback = process_data_events_callback

    def queue_declare(self, queue=None, exclusive=False):

        class _m(object):
            @property
            def method(self):
                return MethodMock(queue)

        self._queues[queue] = []
        return _m()

    def basic_consume(self, fn, queue, no_ack=None):
        self._funcs[queue] = fn

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
            self._corr_id = properties.correlation_id
            self._queues[routing_key].append(body)

    @property
    def connection(self):

        class _c(object):
            def process_data_events(s):
                self._process_data_events_callback(self._corr_id)
                pass

        return _c()

    def mock_get_queue(self, routing_key):
        return self._queues.get(routing_key)

    def mock_clear_queue(self, routing_key=None):
        if routing_key:
            self._queues[routing_key] = []
        else:
            _keys = self._queues.keys()
            self._queues = dict([(x, []) for x in _keys])
