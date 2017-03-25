class VisaGeneralError(Exception):
    """General exception, raised by VDP API.

    This class is inherited throughout module and implements general exception handling, such as error messages
    display.

    :param requests.Response result: Required. Response from VDP.
    """
    def __init__(self, result):

        if result.content:
            self.message = result.content.decode('utf-8')
        else:
            self.message = "Unknown VISA Error"

    def __str__(self):
        return self.message


class VisaTimeoutError(VisaGeneralError):
    """Raised when POST request is timed out.

    This exception is somewhat special, since while being a timeout error, it is in fact a standard response in case
    multiple transactions were submitted, e.g. through `pullfunds.send(multi=True)` call.

    It returns 202 HTTP code which indicates, that request is received and being processed under the hood, the content
    is a transaction ID which can be used in `get` requests to get a status on this specific submission.

    .. note::
        * VISA API HTTP Code: 202
        * VISA Error Code: None
    """


class VisaDuplicateTransactionError(VisaGeneralError):
    """Raised when duplicate transaction detected.

    .. note::
        * VISA API HTTP Code: 303
        * VISA Error Code: None
    """


class VisaMessageValidationError(VisaGeneralError):
    """Raised when message validation error occured.

    .. note::
        * VISA API HTTP Code: 400
        * VISA Error Code: 3001
    """


class VisaUnauthenticatedError(VisaGeneralError):
    """Raised when client is not authenticated.

    .. note::
        * VISA API HTTP Code: 401
        * VISA Error Code: 9123, 9124
    """


class VisaInvalidCertificateError(VisaGeneralError):
    """Raised when client presented invalid certificate.

    .. note::
        * VISA API HTTP Code: 401
        * VISA Error Code: 9125
    """


class VisaAccessDeniedError(VisaGeneralError):
    """Raised when access to resource is restricted.

    .. note::
        * VISA API HTTP Code: 403
        * VISA Error Code: 9611
    """


class VisaNotFoundError(VisaGeneralError):
    """Raised when resource not found.

    .. note::
        * VISA API HTTP Code: 404
        * VISA Error Code: None
    """


class VisaInvalidPanError(VisaGeneralError):
    """Raised with invalid PAN.

    .. note::
        * VISA API HTTP Code: 404
        * VISA Error Code: 3001
    """
