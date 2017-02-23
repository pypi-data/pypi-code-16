# -*- coding: utf-8 -*-

"""Contains the data model structure."""

from __future__ import absolute_import

from byte.compat import add_metaclass
from byte.property import Property, RelationProperty
from byte.registry import Registry

import inspect


class ModelInternal(object):
    """Private structure for internal data model attributes."""

    def __init__(self):
        """Create internal data model structure."""
        self.primary_key = None

        # Private attributes
        self._properties_by_key = None
        self._properties_by_name = None

    @property
    def properties_by_key(self):
        """Retrieve model properties by key."""
        return self._properties_by_key

    @properties_by_key.setter
    def properties_by_key(self, value):
        """Update model properties by key."""
        self._properties_by_key = value
        self._properties_by_name = dict([(prop.name, prop) for prop in value.values()])

    @property
    def properties_by_name(self):
        """Retrieve model properties by name."""
        return self._properties_by_name


class ModelOptions(object):
    """Private structure for data model options."""

    def __init__(self, items=None):
        """
        Create data model options structure.

        :param items: Options dictionary
        :type items: dict
        """
        self.items = items or {}

    @property
    def collection(self):
        """Retrieve model collection."""
        return self.items.get('collection')

    @property
    def slots(self):
        """Retrieve flag indicating model slots have been enabled."""
        return self.items.get('slots', False)

    @classmethod
    def parse(cls, value):
        """
        Parse model options from dictionary or object.

        :param value: Options
        :type value: dict or object
        """
        if not value:
            return cls()

        if type(value) is dict:
            return cls(value)

        options = {}

        for key in dir(value):
            if key.startswith('_'):
                continue

            options[key] = getattr(value, key)

        return cls(options)


class ModelProperties(object):
    """Private structure for data model properties."""

    def __init__(self, properties):
        """
        Create data model properties structure.

        :param properties: Properties dictionary
        :type properties: dict
        """
        self.__all__ = properties

        for key, value in properties.items():
            setattr(self, key, value)

    @classmethod
    def extract(cls, namespace):
        """
        Extract model properties from namespace.

        :param namespace: Class namespace
        :type namespace: dict
        """
        properties = {}

        # Extract properties from `Properties` child class
        if 'Properties' in namespace:
            for key in dir(namespace['Properties']):
                if key.startswith('_'):
                    continue

                value = getattr(namespace['Properties'])

                if not isinstance(value, Property):
                    continue

                # Store property in dictionary
                properties[key] = getattr(namespace['Properties'], key)

        # Extract properties from model
        for key in list(namespace.keys()):
            if key.startswith('_'):
                continue

            if key in properties:
                raise ValueError("Duplicate property '%s' defined on model" % (key,))

            value = namespace[key]

            if not isinstance(value, Property):
                continue

            # Store property in dictionary
            properties[key] = value

            # Delete attribute from model
            del namespace[key]

        return cls(properties)


class ModelMeta(type):
    """Data model metaclass."""

    def __new__(self, name, bases, namespace):
        """
        Create data model class.

        :param name: Class name
        :type name: str

        :param bases: Class bases
        :type bases: tuple

        :param namespace: Class namespace
        :type namespace: dict
        """
        if not bases or bases[0] is object:
            return super(ModelMeta, self).__new__(self, name, bases, namespace)

        internal = namespace['Internal'] = ModelInternal()
        options = namespace['Options'] = ModelOptions.parse(namespace.pop('Options', None))
        properties = namespace['Properties'] = ModelProperties.extract(namespace)

        # Initialize `__slots__` (if enabled)
        if options.slots:
            slots = set(namespace.get('slots', []) + [
                '__collection__'
            ])

            for key, prop in properties.__all__.items():
                if prop.relation:
                    slots.add(key + '_id')  # Identifier property
                    slots.add('_RelationProperty_' + key)  # Resolution cache
                else:
                    slots.add(key)

            namespace['__slots__'] = tuple(slots)

        # Define `objects` on class
        collection = None

        if options.collection:
            collection = namespace['Objects'] = options.collection
        else:
            namespace['Objects'] = None

        # Bind methods
        namespace['__init__'] = self.create_init(bases, namespace, internal, properties)

        # Construct class
        cls = type.__new__(self, name, bases, namespace)

        # Register model class
        Registry.register_model(cls)

        # Bind collection to model
        if collection:
            collection.bind(cls)

        # Bind properties to model
        for key in list(properties.__all__.keys()):
            prop = properties.__all__[key]

            # Generate relation properties
            if prop.relation:
                prop.bind(cls, key + '_id')

                p_id = Property(prop.relation.value_type)
                p_id.bind(cls, key + '_id')

                p_relation = RelationProperty(p_id, prop.value_type)
                p_relation.bind(cls, key)

                # Store relation property on object
                setattr(cls, key, p_relation)

                # Store id property on `Properties`
                setattr(properties, key + '_id', p_id)
                properties.__all__[key + '_id'] = p_id

                # Delete relation property from `Properties
                delattr(properties, key)
                del properties.__all__[key]
                continue

            # Bind property to model
            prop.bind(cls, key)

            # Define primary key on `Internal` class
            if prop.primary_key:
                if internal.primary_key:
                    raise ValueError('Multiple primary key properties are not permitted')

                internal.primary_key = prop

        # Define properties on `Internal` class
        internal.properties_by_key = properties.__all__

        return cls

    @staticmethod
    def create_init(bases, namespace, internal, properties):
        """
        Create model initialization method.

        :param bases: Class bases
        :type bases: tuple

        :param namespace: Class namespace
        :type namespace: dict

        :param internal: Model internal attributes
        :type internal: byte.model.ModelInternal

        :param properties: Model properties
        :type properties: byte.model.ModelProperties

        :return: Initialization function
        :rtype: function
        """
        original = namespace.get('__init__')

        def __init__(self, *args, **kwargs):
            self.__collection__ = kwargs.pop('_collection', None)

            # Set initial property values
            for key, prop in properties.__all__.items():
                # Resolve default value
                if inspect.isfunction(prop.default):
                    value = prop.default()
                else:
                    value = prop.default

                # Set default value for property
                setattr(self, key, kwargs.get(key, value))

            # Call original or super `__init__` method
            if original:
                original(self, *args, **kwargs)
            elif bases[0] is not object:
                bases[0].__init__(self, *args, **kwargs)

        return __init__


@add_metaclass(ModelMeta)
class Model(object):
    """Base data model class."""

    __slots__ = []

    def __init__(self, **kwargs):
        """Create data model item."""
        # Set properties on object (without validation)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def create(cls, **kwargs):
        """Create model item, validate provided properties and save it to the collection (if defined)."""
        item = cls(**kwargs)

        # TODO Validate values against property types

        # Save item to collection (if defined)
        if cls.Options.collection:
            item.save()

        return item

    @classmethod
    def from_plain(cls, data, strict=True, translate=False):
        """
        Parse model item from plain dictionary.

        :param data: Item data
        :type data: dict

        :param strict: Enable strict model parsing (errors will raise exceptions)
        :type strict: bool

        :param translate: Enable data type translation (parse simple types into python data types)
        :type translate: bool

        :return: Model item
        :rtype: byte.model.Model
        """
        properties_by_name = cls.Internal.properties_by_name

        obj = cls()

        for name, value in data.items():
            # Find matching property (by name)
            prop = properties_by_name.get(name)

            if not prop:
                if strict:
                    raise ValueError('Unknown property: %s' % (name,))

                continue

            # Decode value
            try:
                value = prop.decode(value, translate=translate)
            except Exception as ex:
                if strict:
                    raise ValueError('Unable to decode value provided for property: %s - %s' % (name, ex))

                continue

            # Validate against property type
            if not prop.validate(value):
                if strict:
                    raise ValueError('Invalid value provided for property: %s' % (name,))

                continue

            # Set property value
            prop.set(obj, value)

        return obj

    def save(self):
        """Save model item to collection."""
        collection = self.__collection__ or self.__class__.Options.collection

        if not collection:
            raise Exception('Object hasn\'t been bound to any collection')

        collection.insert(self)

    def to_plain(self, translate=False):
        """
        Dump model item to plain dictionary.

        :param translate: Enable data type translation (convert python data types into simple types)
        :type translate: bool

        :return: Plain dictionary
        :rtype: dict
        """
        result = {}

        for name, prop in self.__class__.Internal.properties_by_name.items():
            result[name] = prop.encode(prop.get(self), translate=translate)

        return result

    def __repr__(self):
        """Retrieve string representation of model item."""
        class_name = self.__class__.__name__
        primary_key = self.__class__.Internal.primary_key

        if primary_key:
            return '<%s %s: %r>' % (
                class_name,
                primary_key.key,
                primary_key.get(self)
            )

        return '<%s>' % class_name
