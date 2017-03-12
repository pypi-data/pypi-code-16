import uuid

from ea.cqrs.command.request import Request
from ea.cqrs.exc import CommandRejected
from ea.cqrs.command.issuer.base import ICommandIssuer
import ea.lib.timezone


class LocalCommandIssuer(ICommandIssuer):
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
        req = Request.factory(cmd, sync=sync,
            cid=cid, issuer=issuer)
        return self.issue(req)

    def issue(self, request):
        handler = request.load(self.provider)
        return self.runner.run(request, handler)

    def reject(self, cmd):
        """Reject a command."""
        raise self.Rejected(cmd, cmd.errors)
