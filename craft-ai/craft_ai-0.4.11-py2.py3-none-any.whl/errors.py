class CraftAIError(Exception):
    """Base class for exceptions in the craft ai client."""
    def __init__(self, message):
        super(CraftAIError, self).__init__(message)

    def __str__(self):
        return repr(self.message)


class CraftAIUnknownError(CraftAIError):
    """Raised when an unknown error happens in the craft ai client."""
    def __init__(self, message):
        self.message = "".join(("Unknown error occured. ", message))
        super(CraftAIError, self).__init__(message)


class CraftAINetworkError(CraftAIError):
    """Raised when a network error happens between the client and craft ai"""
    def __init__(self, message):
        self.message = "".join(("Network issue: ", message))
        super(CraftAIError, self).__init__(message)


class CraftAICredentialsError(CraftAIError):
    """Raised when the given credentials for a request or the global config
    aren't valid """
    def __init__(self, message):
        self.message = "".join((
            "Credentials error: ",
            message
        ))
        super(CraftAIError, self).__init__(message)


class CraftAIInternalError(CraftAIError):
    """Raised when an Internal Server Error (500) happens on craft ai's side"""
    def __init__(self, message):
        self.message = "".join(("Internal error occured", message))
        super(CraftAIError, self).__init__(message)


class CraftAIBadRequestError(CraftAIError):
    """Raised when the asked request is not valid for craft ai's API"""
    def __init__(self, message):
        self.message = "".join(("Bad request: ", message))
        super(CraftAIError, self).__init__(message)


class CraftAINotFoundError(CraftAIError):
    """Raised when craft ai answers with a Not Found Error (404)"""
    def __init__(self, message, obj="URL"):
        self.message = "".join((obj, " not found: ", message))
        super(CraftAIError, self).__init__(message)


class CraftAIDecisionError(CraftAIError):
    """Raised when some issue is encountered when trying to find a decision"""
    def __init__(self, message):
        self.message = "".join(("Can't make a decision: ", message))
        super(CraftAIError, self).__init__(message)


class CraftAITimeError(CraftAIError):
    """Raised when trying to create a time object fails"""
    def __init__(self, message):
        self.message = "".join(("Can't create time object: ", message))
        super(CraftAIError, self).__init__(message)
