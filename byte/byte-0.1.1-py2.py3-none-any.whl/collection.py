# -*- coding: utf-8 -*-

"""Contains the collection structure for the storage of keyed items."""


class Collection(object):
    """Collection for the storage of keyed items."""

    def __init__(self, model=None):
        """
        Create keyed item collection.

        :param model: Collection data model
        :type model: byte.model.Model
        """
        self.model = model

        self.items = {}

        # Load collection (if model provided)
        if model:
            self.reload()

    @property
    def internal(self):
        """Retrieve internal model metadata."""
        if not self.model:
            return None

        return self.model.Internal

    @property
    def properties(self):
        """Retrieve model properties."""
        if not self.model:
            return None

        return self.model.Properties

    def bind(self, model):
        """
        Bind collection to data model.

        :param model: Data model
        :type model: byte.model.Model
        """
        if not model:
            raise Exception('Invalid value provided for the "model" parameter')

        self.model = model
        self.reload()

    def reload(self):
        """Reload collection."""
        if not self.model:
            return False

        # TODO Load collection
        return True

    # region Collection methods

    def get(self, *args, **kwargs):
        """
        Retrieve object matching the provided parameters.

        :param args: Primary key
        :type args: tuple

        :param kwargs: Item parameters
        :type kwargs: dict

        :return: Item
        :rtype: byte.model.Model
        """
        if args:
            if len(args) != 1:
                raise ValueError('Only one positional argument is permitted')

            if kwargs:
                raise ValueError('Positional and keyword arguments can\'t be mixed')

            return self.items.get(args[0])

        raise NotImplementedError

    def get_or_create(self, defaults=None, **kwargs):
        """Try retrieve object matching the provided parameters, create the object if it doesn't exist."""
        raise NotImplementedError

    def create(self, **kwargs):
        """
        Create an object with the provided parameters, and save it to the collection.

        :param kwargs: Item parameters
        :type kwargs: dict
        """
        obj = self.model(_collection=self, **kwargs)
        obj.save()

        return obj

    def insert(self, obj):
        """
        Insert item into the collection.

        :param obj: Instance
        :type obj: byte.model.Model

        :return: Inserted instance
        :rtype: byte.model.Model
        """
        if not isinstance(obj, self.model):
            raise ValueError('Invalid object for collection')

        if not self.internal.primary_key:
            raise Exception('Model has no primary key')

        # Retrieve primary key
        key = self.internal.primary_key.get(obj)

        if key is None:
            raise ValueError('Invalid value for primary key: %r' % (key,))

        # Insert item
        self.items[key] = obj

        return obj

    def bulk_insert(self, objs, batch_size=None):
        """
        Insert multiple items in an efficient manner (usually only one query).

        :param objs: Items
        :type objs: list of byte.model.Model

        :param batch_size: Query batch size
        :type batch_size: int
        """
        raise NotImplementedError

    def update_or_create(self, defaults=None, **kwargs):
        """
        Update object with the given parameters, create an object if it doesn't exist.

        :param defaults: Item defaults
        :type defaults: dict

        :param kwargs: Item parameters
        :type kwargs: dict
        """
        raise NotImplementedError

    def count(self):
        """Retrieve number of currently stored items."""
        raise NotImplementedError

    def iterator(self):
        """Retrieve iterator which yields all currently stored items."""
        raise NotImplementedError

    def latest(self, field_name=None):
        """Retrieve the latest item (by the provided date `field_name`)."""
        raise NotImplementedError

    def oldest(self, field_name=None):
        """Retrieve the oldest item (by the provided date `field_name`)."""
        raise NotImplementedError

    def first(self):
        """Retrieve the first item, or `None` if there is no items."""
        raise NotImplementedError

    def last(self):
        """Retrieve the last item, or `None` if there is no items."""
        raise NotImplementedError

    # endregion
