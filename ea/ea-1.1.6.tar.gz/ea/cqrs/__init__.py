import functools

from ea.cqrs.command import Command
from ea.cqrs.command import CommandHandlerProvider
from ea.cqrs.command import CommandHandler
from ea.cqrs.command import ICommandRunner
from ea.cqrs.command import ICommandResult
from ea.cqrs.command import SoloCommandRunner
from ea.cqrs.command import ICommandIssuer
from ea.cqrs.command import LocalCommandIssuer


def handles(command):
    """A class decorator to be used on a :class:`CommandHandler`
    to indicate which command it handlers.
    """

    def decorator(cls):
        cls.__command__ = command
        cls.command_name = command.meta.name
        return cls
    return decorator
