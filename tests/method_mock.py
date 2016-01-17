class MethodMock(object):
    def __init__(self, routing_key):
        self._routing_key = routing_key

    @property
    def routing_key(self):
        return self._routing_key

    @property
    def delivery_tag(self):
        return ''
