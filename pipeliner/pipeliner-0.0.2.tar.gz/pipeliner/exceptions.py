class RegisterException(Exception):
    pass


class TaskAlreadyRegistered(RegisterException):
    pass


class TaskNotFound(RegisterException):
    pass


class PipelineException(Exception):
    pass


class TaskDependencyError(PipelineException):
    pass


class PipelineAlreadyRunning(PipelineException):
    pass
