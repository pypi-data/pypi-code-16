from ea.event.transport.delivery import DeliverySet


class BaseTransport(object):
    """The base class for all transport implementations."""

    def __init__(self, adapter):
        self.adapter = adapter

    def flush(self):
        """Flushes pending messages. Definition hereof is implementation
        dependent. The default implementation does nothing.
        """
        return

    def send_events(self, events, txid=None):
        results = []
        for dto in events:
            if txid is not None:
                dto.set_transaction_id(txid)
            results.append(self.send(dto.as_message(self.adapter.dump)))

        self.flush()
        return DeliverySet(results)

    def to_message(self, headers, params):
        raise NotImplementedError("Subclasses must override this method.")

    def from_message(self, msg):
        raise NotImplementedError("Subclasses must override this method.")

    def send(self, *args, **kwargs):
        raise NotImplementedError("Subclasses must override this method.")
