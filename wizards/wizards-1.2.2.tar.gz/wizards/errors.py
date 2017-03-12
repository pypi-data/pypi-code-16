import copy

from ea.lib.datastructures import ImmutableDTO


class ErrorMessageProvider:
    """Provides prefedined error messages."""
    defaults = ImmutableDTO({
        'HTTP_METHOD_NOT_ALLOWED': {
            'code': "HTTP_METHOD_NOT_ALLOWED",
            'status': 405,
            'message': (
                "The method specified by the request is not allowed. "
            ),
            'hint': "Consult the API specification.",
        },
        'HTTP_NOT_ACCEPTED': {
            'code': "HTTP_NOT_ACCEPTED",
            'status': 406,
            'message': (
                "The server is not able to generate responses using the "
                "content type specified in the Accept header. "
            ),
            'hint': "Consult the API specification.",
        },
        'AUTHENTICATION_REQUIRED': {
            'code': "AUTHENTICATION_REQUIRED",
            'status': 401,
            'message': "Authentication is required to access this resource."
        },
        'DTO_VALIDATION_ERROR': {
            'code': "DTO_VALIDATION_ERROR",
            'status': 422,
            'message': (
                "The input parameters were not valid "
            ),
        },
        'RESOURCE_DOES_NOT_EXIST': {
            'code': "RESOURCE_DOES_NOT_EXIST",
            'status': 404,
            'message': (
                "The requested resource does not exist. "
            ),
            'hint': "Consult the API specification.",
        },
    })

    @property
    def messages(self):
        return self.defaults | self.provided

    def __init__(self):
        self.provided = {}
        self.defaults = self.defaults.as_dto()

    def get(self, code):
        return copy.deepcopy(self.messages[code])

    def register(self, message):
        """Register a new error message."""
        message = ImmutableDTO(message)
        self.provided[message.code] = message


__provider = ErrorMessageProvider()
del ErrorMessageProvider
get = __provider.get
register = __provider.register
