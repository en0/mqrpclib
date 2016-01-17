class ChannelMock(object):

    def basic_publish(self, exchange, routing_key, properties, body):
        pass

    def queue_declare(self, name=None, exclusive=False):
        pass

    def basic_consume(self, fn, queue, no_ack=False):
        pass

    @property
    def connection(self):
        class _mock(object):
            def process_data_events(self):
                pass
        return _mock
