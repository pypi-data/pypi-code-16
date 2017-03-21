class KikError(Exception):
    """
    Exception raised by all API errors.
    The exception message is set to the server's response.

    :param status_code: Status code returned by the API call
    :type status_code: int
    :param content: Content returned by the API call
    :type content: string
    """
    def __init__(self, message, status_code, content=None):
        super(KikError, self).__init__(message)
        self.status_code = status_code
        self.content = content
