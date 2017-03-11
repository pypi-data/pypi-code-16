from ea.cqrs.command.runner.base import ICommandRunner
from ea.cqrs.command.runner.base import ICommandResult


class SoloCommandRunner(ICommandRunner):
    """An :class:`~ea.cqrs.ICommandRunner` implementation that
    executes the command handler in the local thread.
    """

    def run(self, request, handler):
        cmd = request.get_command(handler.command_class)
        return handler(request.headers, cmd.params)
