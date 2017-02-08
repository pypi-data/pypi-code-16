"""
    authorization_levels
    ~~~~~~~~~~~~~~~~~~~~

    This module defaines all authorization levels we know.

    Code of conduct
    ---------------

    Other Datapunt services depend on these levels. When editing this file,
    keep in mind that:

    - the LEVEL_* prefix has significance and is used to fetch all supported
      levels from this module (i.e.
      `{level for level in dir(authorization_levels) if level[:6] == 'LEVEL'}`)
    - LEVEL_DEFAULT has special significance, and its value nor its name can be
      changed without breaking downstream projects.

"""

LEVEL_DEFAULT = 0b0
""" All users have at least this level
"""

LEVEL_EMPLOYEE = 0b1
LEVEL_EMPLOYEE_PLUS = 0b11


def is_authorized(granted, needed):
    """ Authorization function, checks whether the user's `granted` authz level
    is sufficient for that `needed`.

    :return bool: True is sufficient, False otherwise
    """
    return needed & granted == needed
