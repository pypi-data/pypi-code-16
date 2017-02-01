class ConfigException(Exception):
    def __init__(self, message=None):
        super().__init__(message)


class ConfigNotFoundException(ConfigException):
    def __init__(self, message=None):
        super().__init__(message)


class ValueMissingException(ConfigException):
    def __init__(self, message):
        super().__init__(message)


class InvalidValueException(ConfigException):
    pass
