# Copyright 2017 Graham Binns. This software is licensed under the MIT
# license. See the LICENSE file for more information.
"""A utility for describing enums in a DRY and Django style."""

import re


__metaclass__ = type

__all__ = [
    "Enum",
]


VALID_PYTHON_NAME_REGEX = re.compile("^[A-Z_][A-Z0-9_]*$")


class Enum:
    """Describes an enumerated set of items in various forms."""

    def __init__(self, *args):
        """Create a new Enum from passed arguments.

        Each argument can be either a 3-tuple of (id, python_name,
        display_name) or a two-tuple of (python_name, display_name). In
        the latter case, IDs are assigned as the Enum is created.

        Two-tuple and three-tuple forms cannot be mixed; trying to do so
        will raise a ValueError.
        """
        self._last_id = None
        self._id_mappings = {}
        self._display_name_mappings = {}

        last_arg_length = None
        for item in args:
            if last_arg_length is None:
                last_arg_length = len(item)
            elif len(item) != last_arg_length:
                raise ValueError(
                    "You can't mix 2- and 3-tuples when creating an Enum.")

            if len(item) == 2:
                id = next(self.ids)
                python_name, display_name = item
            else:
                id, python_name, display_name = item

            if not VALID_PYTHON_NAME_REGEX.match(python_name):
                raise ValueError(
                    "python_name `{0}` is invalid.".format(python_name))

            self._id_mappings[python_name] = id
            self._display_name_mappings[id] = display_name

    @property
    def ids(self):
        """A generator that yields linearly-increasing integers."""
        if self._last_id is None:
            self._last_id = 0
        else:
            self._last_id += 1
        yield self._last_id

    def __getattr__(self, name):
        """For a given `name` return correct ID value, assuming that
        name is registered.

        If `name` is not registered, raise an AttributeError.
        """
        if name not in self._id_mappings:
            raise AttributeError(
                "Enum does not have a key '{0}'.".format(name))
        return self._id_mappings[name]

    def as_choices(self):
        """Return this Enum's items as tuple of Django choices."""
        keys = sorted(self._display_name_mappings.keys())
        return tuple(
            (id, self._display_name_mappings[id]) for id in keys)
