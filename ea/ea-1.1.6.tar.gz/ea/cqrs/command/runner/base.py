

class ICommandRunner:
    """The base class for all command runners."""

    def run(self, request, handler):
        """Run the command contained in `request` using
        :class:`~ea.cqrs.CommandHandler` implementation `handler`.
        Return a :class:`~ea.cqrs.ICommandResult` instance.
        """
        raise NotImplementedError("Subclasses must override this method.")


class ICommandResult:
    """The base class for all result wrappers returned by the
    :meth:`~ea.cqrs.ICommandRunner.run()` method.
    """

    @property
    def result(self):
        raise NotImplementedError("Subclasses must override this method.")

    def wait(self, timeout=None):
        raise NotImplementedError("Subclasses must override this method.")
