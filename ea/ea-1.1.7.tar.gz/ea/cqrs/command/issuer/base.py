

class ICommandIssuer:

    def put(self, cmd, sync=False):
        """Issue a command to the command handler.

        The `sync` argument may be used to request synchronous
        execution of the command handler, meaning that :meth:`put()`
        will block until it returns.
        """
        raise NotImplementedError("Subclasses must override this method.")
