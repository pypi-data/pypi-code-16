from ea.event.schema import IncomingEventHeaderSchema


class EventValidator(object):
    schema = IncomingEventHeaderSchema()

    def validate_headers(self, event_type, headers):
        """Validate the headers of an incoming event."""
        _, errors = self.schema.load(headers)
        return errors

    def validate_params(self, event_type, params):
        """Validate the parameters of an incoming event."""
        return {}
