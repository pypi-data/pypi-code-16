import uuid

from ea.lib import timezone
from ea.lib.datastructures import ImmutableDTO
from ea.exc import ImplementationError


class EventDTO(object):
    """The Data Transfer Object (DTO) containing an event, both
    the headers and the parameters.
    """

    @property
    def protocol_version(self):
        return self.__headers.get('protocol_version')

    @property
    def id(self):
        return self.__headers.get('id')

    @property
    def type(self):
        return self.event_type

    @property
    def cid(self):
        return self.__headers.get('cid')

    @property
    def tid(self):
        return self.__headers.get('transaction_id')

    @property
    def transaction_id(self):
        return self.__headers.get('transaction_id')

    @property
    def priority(self):
        return self.__headers.get('priority')

    @property
    def received(self):
        return self.__headers.get('received')

    @property
    def timestamp(self):
        return self.__headers.get('timestamp')

    @property
    def headers(self):
        return ImmutableDTO(self.__headers)

    @property
    def params(self):
        return ImmutableDTO(self.__params)

    @property
    def event_type(self):
        return self.__headers.get('type')

    @property
    def errors(self):
        return ImmutableDTO(self.__errors)

    def __init__(self, headers, params):
        headers.setdefault('id', str(uuid.uuid4()))
        self.__headers= headers
        self.__params = params
        self.__errors = {}

    def mark_published(self):
        """Set the timestamp of publication to the current date
        and time.
        """
        self.__headers['timestamp'] = timezone.now()

    def set_received(self, timestamp):
        """Set the date and time at which the event was received
        by the gateway.
        """
        self.__headers['received'] = timestamp

    def set_transaction_id(self, txid):
        """Sets the transaction id, identifying the transaction in
        which the event was published.
        """
        self.__headers['transaction_id'] = txid

    def as_message(self, adapter):
        """The :meth:`as_message` converts an :class:`EventDTO` instance
        to a Python object that is recognized by the underlying AMQP
        library, using `adapter`. This is a callable that receives a
        plain dictionary as its argument, containing the keys ``headers``
        and ``params``.
        """
        return adapter(headers=self.__headers, params=self.__params)

    def is_rejected(self, validator):
        """Return a boolean indicating if the event is rejected."""
        errors = validator.validate_params(self.event_type, self.__params)
        if errors:
            self.__errors['params'] = errors

        return bool(errors)

    def is_invalid(self, validator):
        """Return a boolean indicating if the event message
        contained valid headers.
        """
        errors = validator.validate_headers(self.event_type, self.__headers)
        if errors:
            self.__errors['headers'] = errors

        return bool(errors)

    def is_valid(self, validator):
        """Return a boolean indicating if the event is valid."""
        valid = not self.is_invalid(validator) and not self.is_rejected(validator)
        if valid:
            self.__headers['timestamp'] = timezone.now()
        return valid

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return "<EventDTO: %s>" % self.id
