

class ICommandResult(object):
    """The base class for all command result implementations."""
    CommandExecutionTimeout = type('CommandExecutionTimeout', (Exception,), {})

    def wait(self, timeout=None):
        """Wait until the command has been executed and return its
        result. The optional `timeout` parameter specifies the timeout
        in milliseconds before raising a :exc:`CommandExecutionTimeout`
        exception.
        """
        raise NotImplementedError("Subclasses must override this method.")
