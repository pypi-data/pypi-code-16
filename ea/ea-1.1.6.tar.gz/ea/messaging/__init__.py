try:
    from ea.messaging.registry import Registry
except ImportError as e:
    if e.name != 'proton':
        raise

    from ea.utils import MissingDependency

    Registry = MissingDependency(e)


class AMQPMessageHandler:

    def wants(self, msg):
        return True

    def handle(self, msg):
        raise NotImplementedError("Subclasses must override this method.")
