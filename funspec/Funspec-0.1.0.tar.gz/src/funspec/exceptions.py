from iospec.exceptions import BuildError, ExecutionError


class AnswerKeyError(Exception):
    """
    Raised when there is a problem in a answer key definition.
    """