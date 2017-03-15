class ValidationError(Exception):
    pass


class TransUnionAPIError(Exception):
    pass


class InvalidResponse(TransUnionAPIError):
    def __init__(self, data):
        message = 'Unrecognized response.'
        msg = '{} illformatted: {}'.format(message, str(data))
        super(InvalidResponse, self).__init__(msg)


class InvalidCredentials(TransUnionAPIError):
    def __init__(self, endpoint_url):
        message = 'invalid credentials for {}'.format(endpoint_url)
        super(InvalidCredentials, self).__init__(message)
