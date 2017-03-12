import uuid

from ea.lib import timezone
from ea.event.dto import EventDTO


class NullFactory(object):
    """An :class:`EventFactory` implementation that performs
    no validation and only creates the event Data Transfer
    Object (DTO).
    """

    def create(self, event, **headers):
        """Create a new :class:`~ea.event.dto.EventDTO` instance."""
        headers.setdefault('cid', str(uuid.uuid4()))
        headers.setdefault('occurred', timezone.now())
        headers['type'] = event.meta.name
        return EventDTO(headers, event.dump())
