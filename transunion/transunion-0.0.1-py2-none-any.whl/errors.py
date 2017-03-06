class ValidationError(Exception):
    pass


class TransUnionAPIError(Exception):
    pass


class IllFormattedResponse(TransUnionAPIError):
    def __init__(self, data):
        message = 'Unrecognized response.'
        msg = '{} illformatted: {}'.format(message, str(data))
        super(IllFormattedResponse, self).__init__(msg)
