class PropMock(object):
    def __init__(self, reply_to, correlation_id):
        self._reply_to = reply_to
        self._correlation_id = correlation_id

    @property
    def correlation_id(self):
        return self._correlation_id

    @property
    def reply_to(self):
        return self._reply_to
