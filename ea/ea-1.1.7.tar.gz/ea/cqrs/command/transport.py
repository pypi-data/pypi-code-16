

class ICommandTransport(object):

    def send(self, request):
        """Send the command request to the processing backend. It
        must return an implementation of :class:`ICommandResult`.
        """
        raise NotImplementedError("Subclasses must override this method.")


class LocalTransport(ICommandTransport):
    """An :class:`ICommandTransport` implementation that runs
    the command locally.
    """

    @property
    def provider(self):
        return self._provider


    @property
    def runner(self):
        return self._runner

    def __init__(self, provider=None, runner=None):
        self._provider = provider
        self._runner = runner

    def send(self, request):
        return self.runner.run(request, request.get_handler(self.provider))
