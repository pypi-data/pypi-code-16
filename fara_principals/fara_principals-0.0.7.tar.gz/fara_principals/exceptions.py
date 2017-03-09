class FaraException(Exception):
    """
    Base exception class for this software
    """
    pass


class PrincipalError(FaraException):
    """
    Raised when there is a problem with a principal data
    """
    pass

class InvalidPrincipalError(PrincipalError):
    """
    Raise when the schema for a principal does not contain certain required
    fields.
    """
    pass

class InvalidExhibitError(PrincipalError):
    """
    Raise when the schema for an Exhibit does not contain certain required
    fields.
    """
    pass

class PageError(FaraException):
    """
    Raised when an error which relates to a page is encountered e.g, when
    certain important details cant be found on a page.
    """
    pass

class PageInstanceInfoNotFoundError(PageError):
    """
    Raised when information about the server-tracked details are not found
    on a page which is meant to contain those details.
    """
    pass

class PaginationEndedError(PageError):
    """
    Raised when there is no more data on a page
    """
    pass