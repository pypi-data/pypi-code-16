# -*- coding: utf-8 -*-

"""Contains the property structure."""

from byte.compat import string_types
from byte.registry import Registry

from arrow import Arrow
from collections import namedtuple
from datetime import datetime
from decimal import Decimal
import arrow


Translation = namedtuple('Translation', ['encode', 'decode'])

TRANSLATIONS = {
    Arrow: Translation(
        lambda value: value.isoformat(),
        lambda value: arrow.get(value)
    ),
    Decimal: Translation(
        lambda value: str(value),
        lambda value: Decimal(value)
    ),

    datetime: Translation(
        lambda value: arrow.get(value).isoformat(),
        lambda value: arrow.get(value).datetime
    )
}


class Property(object):
    """Property structure."""

    def __init__(self, value_type, by=None, default=None, max_length=None, name=None, nullable=False,
                 primary_key=False):
        """
        Create model property.

        :param value_type: Value type
        :type value_type: object

        :param by: Relation key
        :type by: str

        :param default: Default value
        :type default: object

        :param max_length: Maximum string length
        :type max_length: int

        :param name: Alternative property name for encoding/decoding
        :type name: str

        :param nullable: Accept `None` values
        :type nullable: bool

        :param primary_key: Use property as the primary model key
        :type primary_key: bool
        """
        self.value_type = value_type

        self.by = by

        self.default = default
        self.max_length = max_length
        self.nullable = nullable
        self.primary_key = primary_key

        # Private attributes
        self._name = name
        self._relation = None

        # Bind attributes
        self.model = None
        self.key = None

        # Determine if the property is a model relation
        if self.value_type in Registry.models:
            if self.by is not None:
                if self.by not in self.value_type.Internal.properties_by_key:
                    raise ValueError("Relation '%s' has no '%s' property" % (self.value_type.__name__, self.by))

                self._relation = getattr(self.value_type.Internal.properties_by_key, self.by)
            else:
                if not self.value_type.Internal.primary_key:
                    raise ValueError("Relation '%s' has no primary key" % (self.value_type.__name__,))

                self._relation = self.value_type.Internal.primary_key

    @property
    def name(self):
        """Retrieve name."""
        return self._name or self.key

    @property
    def relation(self):
        """
        Retrieve related model property.
        
        :rtype: byte.property.Property
        """
        return self._relation

    def bind(self, model, key):
        """
        Bind property to model.

        :param model: Model
        :type model: class

        :param key: Property key
        :type key: str
        """
        self.model = model
        self.key = key

    def get(self, obj):
        """
        Retrieve property value from instance.

        :param obj: Instance
        :type obj: byte.model.Model

        :return: Value
        :rtype: object
        """
        if not self.key:
            raise Exception('Property hasn\'t been bound yet')

        return getattr(obj, self.key)

    def set(self, obj, value):
        """
        Update property value on instance.

        :param obj: Instance
        :type obj: byte.model.Model

        :param value: Value
        :type value: object
        """
        if not self.key:
            raise Exception('Property hasn\'t been bound yet')

        setattr(obj, self.key, value)

    def encode(self, value, translate=False):
        """
        Encode property value.

        :param value: Raw value
        :type value: object

        :param translate: Enable data type translation
        :type translate: bool

        :return: Encoded value
        :rtype: object
        """
        if value is None:
            return None

        if translate:
            if self.value_type not in TRANSLATIONS:
                return value

            return TRANSLATIONS[self.value_type].encode(value)

        return value

    def decode(self, value, translate=False):
        """Decode property value.

        :param value: Encoded value
        :type value: object

        :param translate: Enable data type translation
        :type translate: bool

        :return: Raw value
        :rtype: object
        """
        if value is None:
            return None

        if isinstance(value, self.value_type):
            return value

        if translate:
            if self.value_type not in TRANSLATIONS:
                return value

            return TRANSLATIONS[self.value_type].decode(value)

        return value

    def validate(self, value):
        """
        Validate property value.

        :param value: Raw value
        :type value: object

        :return: Boolean indicating the value is valid
        :rtype: bool
        """
        if not self.validate_type(value) and not (value is None and self.nullable):
            return False

        return True

    def validate_type(self, value):
        """
        Validate property value type.

        :param value: Raw value
        :type value: object

        :return: Boolean indicating the value type is valid
        :rtype: bool
        """
        if self.value_type is str:
            return isinstance(value, string_types)

        return isinstance(value, self.value_type)

    def __repr__(self):
        """Retrieve string representation of model property."""
        if not self.model:
            return '<Property (unbound)>'

        tags = []

        if self.primary_key:
            tags.append('primary')

        if self.nullable:
            tags.append('nullable')

        if self.max_length:
            tags.append('max_length(%r)' % self.max_length)

        if self.default:
            tags.append('default(%r)' % self.default)

        return "<Property '%s' on '%s'%s>" % (
            self.key,
            self.model.__name__,
            ' - %s' % (', '.join(tags)) if tags else ''
        )


class RelationProperty(Property):
    """Private relation property structure."""

    def __init__(self, prop, value_type):
        """
        Create model relation property.

        :param prop: Property
        :type prop: byte.property.Property

        :param value_type: Related model
        :type value_type: class
        """
        super(RelationProperty, self).__init__(value_type)

        self.prop = prop

    @property
    def cache_key(self):
        return '_RelationProperty_%s' % self.key

    def get_cache(self, obj):
        return getattr(obj, self.cache_key, None)

    def set_cache(self, obj, value):
        setattr(obj, self.cache_key, value)

    def __get__(self, obj, type=None):
        """
        Retrieve related item.

        :param obj: Instance
        :type obj: byte.model.Model

        :param type: Instance type
        :type type: class

        :return: Related item
        :rtype: byte.model.Model
        """
        value = self.get_cache(obj)

        if value:
            return value

        # Retrieve relation key
        key = self.prop.get(obj)

        if key is None:
            return None

        # Ensure collection exists
        if not self.value_type.Objects:
            raise ValueError("No collection available for '%s'" % (self.value_type.__name__,))

        # Retrieve item from collection
        value = self.value_type.Objects.get(key)

        # Cache relation value
        self.set_cache(obj, value)

        return value

    def __set__(self, obj, value):
        """Update related item.

        :param obj: Instance
        :type obj: byte.model.Model

        :param value: Related item
        :type value: byte.model.Model
        """
        if value is None:
            self.prop.set(obj, value)
            return

        # Update id property
        self.prop.set(obj, self.relation.get(value))

        # Cache relation value
        self.set_cache(obj, value)
