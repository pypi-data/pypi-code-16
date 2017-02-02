#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

import six
from .dictionary import Dictionary
from .utils import ReadOnlyDict, check_keys

_VERTEX_NAME_ATTR = "_name"
_VERTEX_TYPE_ATTR = "_type"
_VERTEX_KEYS_ATTR = "_keys"
_VERTEX_KEYWORDS = "_keywords"


class Vertex(object):
    def __init__(self, vertex_type, name, keys, data=None, **kwargs):
        """
        Defines a client-side vertex. This is basically a set of attributes (with special ones prefixed with '_').

        :param str vertex_type: Vertex type
        :param str name: Name for vertex
        :param dict keys: A set of unique keys identifying this vertex
        :param str primary_key_id: Name of key (within 'keys') designated as primary key (must be globally unique)
        :param dict data: Set of initial values to assign to vertex (optional)
        :param kwargs: Any additional key:value pairs that should be assigned to vertex.
        """
        assert vertex_type, "Type is mandatory"
        assert name, "Name is mandatory"

        check_keys(keys)

        if data is not None:
            assert isinstance(data, dict), "data must be of type dict"
            d = data

        else:
            d = {}

        # Add any keyword args to the dictionary
        if kwargs:
            d.update(kwargs)

        # Get the meta-data from each of the attributes
        for attribute, value in six.iteritems(d):
            stripped_value = Dictionary.update_and_strip(dictionary_type=Dictionary.D_TYPE_VERTEX,
                                                         vertex_key=six.next(six.itervalues(keys)),
                                                         attribute=attribute,
                                                         value=value)
            d[attribute] = stripped_value

        # Add the essentials (to make sure they override everything)
        d.update({
            _VERTEX_TYPE_ATTR: vertex_type,
            _VERTEX_KEYS_ATTR: ReadOnlyDict(keys),
            _VERTEX_NAME_ATTR: name,
        })

        # Finally - update self and set the dirty flag (False as this is the initial setting)
        self._d = d

        self._frozen = False

    def freeze(self):
        # Make sure this vertex is now immutable!
        self._frozen = True
        return self

    @property
    def type(self):
        return self._d[_VERTEX_TYPE_ATTR]

    @property
    def name(self):
        return self._d[_VERTEX_NAME_ATTR]

    @name.setter
    def name(self, name):
        assert not self._frozen, "Vertex is frozen!"
        self[_VERTEX_NAME_ATTR] = name

    @property
    def keys(self):
        """
        :rtype: dict
        :return The vertex keys (DO NOT CHANGE - use add_key instead!!!)
        """
        return ReadOnlyDict(self._d[_VERTEX_KEYS_ATTR])

    @property
    def first_key(self):
        return six.next(six.itervalues(self.keys))

    @property
    def document(self):
        """
        Provides access to internal document representing this vertex

        :rtype: dict[str, str]
        """
        return ReadOnlyDict(self._d)

    def update(self, d):
        """
        Override the default set to handle dirty flag

        :param dict[str, str] d: Dict to update with
        """
        assert not self._frozen, "Vertex is frozen!"
        assert isinstance(d, dict), "Expecting dict"
        assert _VERTEX_KEYS_ATTR not in d, "Cannot update keys!"
        self._d.update(d)

    def __setitem__(self, key, value):
        """
        Override the default set to handle dirty flag
        """
        assert not self._frozen, "Vertex is frozen!"
        assert not key.startswith("_"), "Cannot modify a special/internal attribute"
        self._d.__setitem__(key, value)

    def __getitem__(self, item):
        return self._d.__getitem__(item)

    def __delitem__(self, key):
        assert not key.startswith("_"), "Cannot delete a special/internal attribute"
        return self._d.__delitem__(key)

    def __contains__(self, item):
        return self._d.__contains__(item)

    def get(self, key, default=None):
        return self._d.get(key, default)

    def __eq__(self, other):
        assert isinstance(other, Vertex), "Only Vertex comparisons are supported"
        return self._d == other._d

    def __str__(self):
        return "Vertex ({}) {}: {}".format(self.type, self.name, self.keys)


_EDGE_TYPE_ATTR = "_type"
_EDGE_SOURCE_KEYS_ATTR = "_source_keys"
_EDGE_TARGET_KEYS_ATTR = "_target_keys"


class Edge(object):
    def __init__(self, source, target, edge_type):
        """
        :param Vertex|dict[str, str] source: Vertex or set of vertex keys
        :param Vertex|dict[str, str] target: Vertex or set of vertex keys
        :param str edge_type: Edge type
        """

        source = source.keys if isinstance(source, Vertex) else source
        target = target.keys if isinstance(target, Vertex) else target

        check_keys(source)
        check_keys(target)

        assert source != target, "Source and target are the same (Edge cannot point to itself)"

        self._d = ReadOnlyDict({
            _EDGE_TYPE_ATTR: edge_type,
            _EDGE_SOURCE_KEYS_ATTR: source,
            _EDGE_TARGET_KEYS_ATTR: target,
        })

    def __str__(self):
        return "Edge {}: {} => {}".format(self.type, self.source_keys, self.target_keys)

    @property
    def type(self):
        """ :rtype: str """
        return self._d[_EDGE_TYPE_ATTR]

    @property
    def source_keys(self):
        """ :rtype: dict[str, str] """
        return self._d[_EDGE_SOURCE_KEYS_ATTR]

    @property
    def target_keys(self):
        """ :rtype: dict[str, str] """
        return self._d[_EDGE_TARGET_KEYS_ATTR]

    # noinspection PyProtectedMember
    def __eq__(self, other):
        return self.source_keys == other.source_keys and self.target_keys == other.target_keys

    @property
    def document(self):
        """
        :rtype: dict[str, str]
        :return: Document (Read-only) representing this edge
        """
        return self._d
