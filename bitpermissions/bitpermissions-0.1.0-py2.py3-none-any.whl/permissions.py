import types


class PermissionException(Exception):
    """The required permissions aren't available"""


def build_permission_property(bit_index):
    bit = 1 << bit_index
    doc = "Permission bit is {}".format(bit)

    def get(self):
        """:return: int corresponding to the permission"""
        return self._perms & bit

    def set_(self, boolean):
        if boolean:
            self._perms |= bit
        else:
            self._perms &= ~bit

    return property(get, set_, doc=doc)


class BitField(int):

    def __new__(cls, value, length=None):
        if length is None:
            length = len(bin(value)[2:])
        the_integer = super(BitField, cls).__new__(cls, value)
        the_integer._field_length = length
        return the_integer

    def __repr__(self):
        """Show the rights as a byte string."""
        return '{:0>{}b}b'.format(self, self._field_length)


def build_has_fnc(name):
    def has_fnc_built(self):
        if self.__getattribute__(name):
            pass
        else:
            raise PermissionException("No permission for right '{}'.".format(name))
    return has_fnc_built


class Permissions(object):
    """Bit based permissions"""

    def __init__(self, perms, perm_rights=0):
        """
        :param perms: List of perms to create
        :param perm_rights: type <int> permissions to set (input -1 gives all rights)
        """
        self._num_of_rights = 0

        for perm in perms:
            property_method = build_permission_property(self._num_of_rights)
            setattr(self.__class__, str(perm), property_method)
            has_func = build_has_fnc(perm)
            setattr(self, str('has_' + perm), types.MethodType(has_func, self))
            self._num_of_rights += 1

        # Provide an easy way to give all rights without counting number of perms
        if perm_rights == -1:
            perm_rights = (1 << self._num_of_rights) - 1
        self._perms = int(perm_rights)

    def __repr__(self):
        return self.permissions.__repr__()

    @property
    def permissions(self):
        return BitField(self._perms, self._num_of_rights)

    @permissions.setter
    def permissions(self, perm_digits):
        self._perms = perm_digits
