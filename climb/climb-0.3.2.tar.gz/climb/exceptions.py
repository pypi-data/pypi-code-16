class ConfigNotFound(Exception):
    pass


class CLIException(Exception):
    pass


class UnknownCommand(CLIException):
    pass


class MissingArgument(CLIException):
    pass
