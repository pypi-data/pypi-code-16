from ea.event.schema import OutgoingEventHeaderSchema
from ea.event.dto import EventDTO
from ea.exc import ImplementationError


class BaseAdapter(object):
    """The base class for all adapters."""
    schema = OutgoingEventHeaderSchema()

    def dump(self, headers, params):
        raise NotImplementedError("Subclasses must override this method.")

    def get_headers(self, msg):
        raise NotImplementedError("Subclasses must override this method.")

    def get_body(self, msg):
        raise NotImplementedError("Subclasses must override this method.")

    def load(self, msg):
        """Load an incoming event from an incoming message."""
        headers, errors = self.schema.load(self.get_headers(msg))
        if errors:
            raise ImplementationError(errors)

        return EventDTO(headers, self.get_body(msg))


class DictAdapter(BaseAdapter):
    schema = OutgoingEventHeaderSchema()

    def dump(self, headers, params):
        headers, errors = self.schema.dump(headers)
        if errors:
            raise ImplementationError(errors)
        return {'headers': headers, 'params': params}

    def get_headers(self, msg):
        return msg['headers']

    def get_body(self, msg):
        return msg['params']
