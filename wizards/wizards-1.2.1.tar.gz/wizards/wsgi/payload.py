

class ResponsePayload:
    """A wrapper around a response payload used by the serializer
    to determine the content type to send over the wire.
    """

    def __init__(self, body):
        self.body = body

    def __serialize__(self, f):
        return f(self.body)
