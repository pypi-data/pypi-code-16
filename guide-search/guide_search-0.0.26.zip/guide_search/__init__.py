__version__ = '0.0.23'
__author__ = 'John Pickerill <john.pickerill@landregistry.gov.uk>'
__all__ = ['Esearch', 'Dsl',  'ResourceNotFoundError']


from guide_search.esearch import Esearch
from guide_search.dsl import Dsl

from guide_search.exceptions import (    # noqa: F401
    BadRequestError,            # 400
    ResourceNotFoundError,      # 404
    ConflictError,              # 409
    PreconditionError,          # 412
    ServerError,                # 500
    ServiceUnreachableError,    # 503
    UnknownError,               # unexpected http response
    ResultParseError,           # es result not in expected form
    CommitError,
    JSONDecodeError,
    ValidationError)
__version__ = '0.0.26'
__author__ = 'John Pickerill <john.pickerill@landregistry.gov.uk>'
__all__ = ['Esearch', 'Dsl',  'ResourceNotFoundError']
