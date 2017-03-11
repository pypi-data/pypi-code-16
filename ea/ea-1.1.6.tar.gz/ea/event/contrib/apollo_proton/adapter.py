import uuid

from proton import Message

from ea.event.transport import BaseAdapter
from ea.exc import ImplementationError


class ProtonAdapter(BaseAdapter):

    def get_headers(self, msg):
        return msg.properties

    def get_body(self, msg):
        return msg.body

    def dump(self, headers, params):
        """Dump an outgoing event to a :class:`proton.Message`
        instance.
        """
        properties, errors = self.schema.dump(headers)
        if errors:
            raise ImplementationError(errors)
        return Message(id=str(uuid.uuid4()),
            properties=dict(properties),
            body=dict(params)
        )
