from guide_search._version import  __version__, __author__
from guide_search.esearch import Esearch
from guide_search.dsl import Dsl

from guide_search.exceptions import (    # noqa: F401
    BadRequestError,            # 400
    ResourceNotFoundError,      # 404
    ConflictError,              # 409
    PreconditionError,          # 412
    ServerError,                # 500
    ServiceUnreachableError,    # 503
    UnknownError,               # unexpected htstp response
    ResultParseError,           # es result not in expected form
    CommitError,
    JSONDecodeError,
    ValidationError)

__all__ = ['Esearch', 'Dsl',  'ResourceNotFoundError']
