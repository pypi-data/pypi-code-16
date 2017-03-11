import uuid

from ea.cqrs.command.request import Request
from ea.cqrs.exc import CommandRejected
import ea.lib.timezone


class CommandIssuer:

    def put(self, cmd, sync=False):
        """Issue a command to the command handler.

        The `sync` argument may be used to request synchronous
        execution of the command handler, meaning that :meth:`put()`
        will block until it returns.
        """
        raise NotImplementedError("Subclasses must override this method.")


class LocalCommandIssuer(CommandIssuer):
    """A :class:`CommandIssuer` implementation that runs
    the command handler in the local thread (i.e. is blocking
    until the handler returns).
    """
    Rejected = CommandRejected

    def __init__(self, provider, runner):
        self.provider = provider
        self.runner = runner

    def put(self, cmd, sync=False, cid=None, issuer=None):
        if not cmd.is_valid():
            self.reject(cmd)

        req = Request(
            id=str(uuid.uuid4()),
            name=cmd.meta.name,
            cid=cid or str(uuid.uuid4()),
            issued=ea.lib.timezone.now(),
            sid=issuer,
            sync=sync
        )
        req.add_command(cmd.dump())

        command_id = str(uuid.uuid4())
        cid = cid or str(uuid.uuid4())

        return self.issue(req)

    def issue(self, request):
        handler = request.load(self.provider)
        return self.runner.run(request, handler)

    def reject(self, cmd):
        """Reject a command."""
        raise self.Rejected(cmd, cmd.errors)
