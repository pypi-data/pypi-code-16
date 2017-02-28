class ResponseException(Exception):
    def __init__(self, message, response, *args, **kwargs):
        self.response = response
        self.http_code = response.status_code
        super(Exception, self).__init__(message, *args, **kwargs)


class SerialiserMapError(Exception):
    def __init__(self, serialiser_key, *args, **kwargs):
        message = '"%s" missing from instance' % serialiser_key[0]
        super(Exception, self).__init__(self, message, *args, **kwargs)
