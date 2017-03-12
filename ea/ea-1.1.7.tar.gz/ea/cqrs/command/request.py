import uuid

from ea.exc import ImplementationError
from ea.lib.datastructures import ImmutableDTO
import ea.lib.timezone
import ea.schema


class Request(object):

    class schema_class(ea.schema.Schema):
        dto_class = ImmutableDTO

        id = ea.schema.fields.UUID(
            required=True,
            load_from='command-id'
        )
        name = ea.schema.fields.String(
            required=True,
            load_from='command-name'
        )
        timestamp = ea.schema.fields.Integer(
            required=True,
            load_from='command-timestamp'
        )
        issuer_id = ea.schema.fields.UUID(
            required=True,
            load_from='command-issuer-id'
        )
        correlation_id = ea.schema.fields.UUID(
            required=True,
            load_from='correlation-id'
        )
        wants_results = ea.schema.fields.Boolean(
            required=False,
            missing=False,
            default=False,
            load_from='command-wants-results'
        )

    schema = schema_class()

    @classmethod
    def factory(cls, cmd, sync, issuer, cid=None):
        return cls(
            cmd.dump(),
            headers= {
                'correlation-id': cid or uuid.uuid4(),
                'command-id': uuid.uuid4(),
                'command-name': cmd.meta.name,
                'command-timestamp': ea.lib.timezone.now(),
                'command-issuer-id': issuer,
                'command-wants-results': not sync
            }
        )

    def __init__(self, cmd, headers):
        self._command_name = None
        self.params = cmd
        self.headers, errors = self.schema.load(headers or {})
        if errors:
            raise ImplementationError(errors)

    def force_handler(self, command_name):
        """Force the request to run the handler for the given
        `command_name`.
        """
        self._command_name = command_name

    def load(self, provider):
        """Loads the handler for the command specified in the
        request.
        """
        return provider.get(self.headers.name)

    def is_valid(self):
        return not bool(self._errors)

    def dump(self):
        return ImmutableDTO({
            "meta": self.schema.dump(self._meta)[0],
            "params": self._params,
            "headers": self._headers
        })

    def get_command(self, cls):
        """Instantiate a new instance of :class:`Command` implementation
        `cls`.
        """
        return cls(**self.params)

    def get_handler(self, provider):
        return provider.get(self._command_name or self._meta['name'])
