"""
Masking HTTP Errors from Django REST Framework
"""

class HTTP_400_BAD_REQUEST(Exception):
    """400 - Bad Request:
    The request was invalid. This response code is common when required
    fields are unspecified, formatted incorrectly,
    or invalid filters are requested.
    """
    pass


class HTTP_401_UNAUTHORIZED(Exception):
    """401 - Unauthorized:
    The request authentication failed. The OAuth credentials that
    the client supplied were missing or invalid.
    """
    pass


class HTTP_403_FORBIDDEN(Exception):
    """403 - Forbidden:
    The request credentials authenticated, but the requesting
    user or client app is not authorized to access the given resource.
    """
    pass


class HTTP_404_NOT_FOUND(Exception):
    """404 - Not Found:
    The requested resource does not exist.
    """
    pass


class HTTP_405_METHOD_NOT_ALLOWED(Exception):
    """405 - Method Not Allowed:
    The requested HTTP method is invalid for the given resource.
    Review the resource documentation for supported methods.
    """
    pass


class HTTP_500_INTERNAL_SERVER_ERROR(Exception):
    """500 - Server Error:
    The server failed to fulfill the request.
    Please notify support with details of the request
    and response so that we can fix the problem.
    """
    pass
