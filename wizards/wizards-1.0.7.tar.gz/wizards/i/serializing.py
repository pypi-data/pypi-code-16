

class Serializable:
    args = []
    kwargs = {}

    def __init__(self, payload):
        self.payload = payload

    def serialize(self, func):
        return func(self.payload, *self.args, **self.kwargs)


class Serializer:
    content_type = None

    def __init__(self):
        if self.content_type is None:
            raise TypeError("Serializer implementations must specify the "
                            "`content_type` attribute.")

    def serialize(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must override this method.")

    def deserialize(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must override this method.")
