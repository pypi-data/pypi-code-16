class SkyWiseModelException(Exception):
    pass


class ModelAlreadyExistsException(SkyWiseModelException):
    pass


class ModelNotFound(SkyWiseModelException):
    pass


class ModelPlatformForecastProductAlreadyExists(SkyWiseModelException):
    pass
