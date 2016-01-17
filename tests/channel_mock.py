class ChannelMock(object):
    def queue_declare(self, queue=None, exclusive=False):
        pass

    def basic_consume(self, fn, queue):
        pass
