import time


class BaseDelivery:
    """A :class:`Delivery` represents a delivery of an event to the
    message broker.
    """

    def settle(self, *args, **kwargs):
        """Mark the delivery as settled."""
        raise NotImplementedError("Subclasses must override this method.")

    def is_settled(self, *args, **kwargs):
        """Return a boolean indicating if the delivery is settled."""
        raise NotImplementedError("Subclasses must override this method.")
        
    def wait(self, timeout=None):
        """Block until the event message is confirmed by the broker."""
        raise NotImplementedError("Subclasses must override this method.")


class NullDelivery(BaseDelivery):
    """A :class:`BaseDelivery` implementation that always returns
    on :meth:`wait()`.
    """

    def settle(self):
        pass

    def is_settled(self):
        return True

    def wait(self, timeout=None):
        return True


class DeliverySet(set):

    def wait(self, timeout=None):
        t1 = time.time()
        for delivery in self:
            if timeout is not None:
                timeout -= (time.time() - t1) * 1000

            if not delivery.is_settled():
                delivery.wait(timeout=timeout)

        return True
