"""
    authorization
    ~~~~~~~~~~~~~

    This package provides an implementation of the Datapunt authorization
    model.
"""


def authz_mapper(**psycopg2conf):
    """ Returns a function that gets a given user's authorization
    level.

    This is a convenient wrapper around an :class:`authz.map.AuthzMap` for
    callers that only want to get an authorization level for a given user, even
    if that user isn't present in the authz table (in which case it will return
    :data:`authz.levels.LEVEL_DEFAULT`).

    Example usage:

    ::

        mapper = authz.authz_mapper(psycopg2conf)
        mapper('username')  # => returns username's authz level

    :param psycopg2conf: See :function:`psycopg2.connect`
    :return: One of LEVEL_* defined in :module:`authz.levels`
    """
    from .map import AuthzMap
    from . import levels

    authzmap = AuthzMap(**psycopg2conf)

    def getter(username):
        return authzmap.get(username, levels.LEVEL_DEFAULT)

    return getter


def is_authorized(granted, needed):
    """ Return True iff the `granted` authz level is sufficient to access
    resources protected with `needed`.

    :param granted: One of LEVEL_* defined in :module:`authz.levels`
    :param needed: One of LEVEL_* defined in :module:`authz.levels`
    :return: True if `granted` is sufficient, False otherwise
    """
    return needed & granted == needed
