"""Base class for all used data models."""
import copy
from pubnub_blocks_client.utils import object_value, set_object_value, is_equal


class Model(object):
    """Model representing class.

    Class used to represent data model and it's properties using passed
    dictionary where access to it provided by key/key-path.
    """

    def __init__(self, data=None, additional_fields=None):
        """Create and configure model data holder.

        :type data:               dict | None
        :param data:              Reference on dictionary which contain
                                  information about model.
        :type additional_fields:  list[str] | None
        :param additional_fields: Additional keys which should be used for
                                  model serialization to dictionary.
        """
        super(Model, self).__init__()
        self._data = copy.deepcopy(data) if data is not None else None
        self._additional_fields = additional_fields or list()

    def keys(self):
        """Model keys.

        Method allow to retrieve list of keys which represent current
        model.
        :rtype:  list[str]
        :return: Name of model fields.
        """
        keys = []
        if self._data:
            keys += list(self._data.keys()) + self._additional_fields

        return keys

    def __getitem__(self, item):
        """Retrieve value for serialization.

        Retrieve value for one of provided keys for further storage in
        resulting dictionary.
        :type item:  str
        :param item: Reference on name of key for which value from model
                     should be retrieved.

        :return: Requested model field value.
        """
        if not self.is_non_property_field(item):
            return self.get_property(item)
        else:
            return self._get_non_property(item)

    @property
    def initialized(self):
        """Stores whether data model has been initialized with data or
        not.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if during model creation data has been
                 passed to storage or not.
        """
        return self._data is not None

    @property
    def is_empty(self):
        """Stores whether model has some data in it or empty.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if there is no data stored in model.
        """
        return not self.initialized or self._data and len(self._data) == 0

    def data(self):
        """Retrieve reference on model storage.

        WARNING: This method should be used internally by module itself.

        :rtype:  dict
        :return: Reference on model storage.
        """
        return self._data or dict()

    def is_non_property_field(self, name):
        """Check whether passed field represent pre-processed data.

        :type name:  str
        :param name: Reference on parameter against which check should be
                     done.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if field has been marked as pre-processed
                 value.
        """
        return name in self._additional_fields

    def get_property(self, name, is_path=False, default=None):
        """Retrieve model value by field name.

        WARNING: This method should be used internally by module itself.

        Retrieve value which is stored in models data storage.
        :type name:     str
        :param name:    Reference on key/path name for which value should
                        be retrieved.
        :type is_path:  bool
        :param is_path: Whether provided field name represent key-path or
                        regular field name.
        :param default: Reference on value which should be used in case if
                        requested field value doesn't exists.

        :return: Stored value or the one which is passed as 'default'.
        """
        return object_value(self._data, name, is_path=is_path, default=default)

    def _get_non_property(self, name):
        """Retrieve one of values which is not part of storage.

        Model able to provide special fields which may require
        pre-processing and returned by request.
        :type name:  str
        :param name: Reference on special field name for which subclass
                     should provide pre-processed data.

        :return: Preprocessed model value for requested field.
        """
        print('{0} unable to provide value for \'{1}\'. '.format(self, name) +
              'This task should be done by subclass.')

    def update(self, data):
        """Update stored model data.

        WARNING: This method should be used internally by module itself.

        :type data:  dict
        :param data: Reference on new information which should be used by
                     model.
        """
        if self._data is None:
            self._data = dict()
        self._data.update(copy.deepcopy(data or dict()))


class MutableModel(Model):
    """Model representing class.

    Class used to represent mutable data model and it's properties using
    passed dictionary where access to it provided by key/key-path.
    """
    def __init__(self, data=None, additional_fields=None):
        """Create and configure mutable model data holder.

        :type data:               dict | None
        :param data:              Reference on dictionary which contain
                                  information about model.
        :type additional_fields:  list[str] | None
        :param additional_fields: Additional keys which should be used for
                                  model serialization to dictionary.
        """
        super(MutableModel, self).__init__(data=data,
                                           additional_fields=additional_fields)
        self._mutable_data = copy.deepcopy(data) if data is not None else None

    def keys(self):
        """Model keys.

        Method allow to retrieve list of keys which represent current
        model.
        :rtype:  list[str]
        :return: Name of model fields.
        """
        keys = super(MutableModel, self).keys()
        if self._mutable_data:
            keys += [key for key in self._mutable_data if key not in keys]

        return keys

    def __getitem__(self, item):
        """Retrieve value for serialization.

        Retrieve value for one of provided keys for further storage in
        resulting dictionary.
        :type item:  str
        :param item: Reference on name of key for which value from model
                     should be retrieved.

        :return: Requested model field value.
        """
        if not self.is_non_property_field(item):
            return self.get_property(item)
        else:
            return self._get_non_property(item)

    @property
    def initialized(self):
        """Stores whether data model has been initialized with data or
        not.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if during model creation data has been
                 passed to storage or not.
        """
        return self._mutable_data is not None

    @property
    def is_empty(self):
        """Stores whether model has some data in it or empty.

        WARNING: This method should be used internally by module itself.

        :rtype:  bool
        :return: 'True' in case if there is no data stored in model.
        """
        is_empty = super(MutableModel, self).is_empty

        return (is_empty or not self.initialized
                or (self._mutable_data and len(self._mutable_data)) == 0)

    def mutable_data(self, mutable=False):
        """Retrieve reference on mutable model storage.

        :type mutable:  bool
        :param mutable: Whether only mutable data should be returned or
                        not.

        WARNING: This method should be used internally by module itself.

        :rtype:  dict
        :return: Reference on model storage.
        """
        immutable_data = super(MutableModel, self).data()
        mutable_data = self._mutable_data or dict()
        final_data = immutable_data
        if not mutable:
            final_data.update(mutable_data)

        return final_data

    def data_changed(self, property_name=None, ignored_fields=None):
        """Check whether mutable object differ from original one.

        WARNING: This method should be used internally by module itself.

        Verify whether any fields of original and mutable objects has been
        changed. If 'property_name' provided only this property will be
        checked for changes.
        :type property_name:   str | None
        :param property_name:  Reference on name of property which should
                               be checked for changes.
        :type ignored_fields:  list[str]
        :param ignored_fields: List of fields which should be removed from
                               compared objects.
        """
        original_data = self._data or dict()
        mutable_data = self._mutable_data or dict()
        if property_name is not None:
            changed = not is_equal(original_data.get(property_name),
                                   mutable_data.get(property_name))
        else:
            if ignored_fields:
                original_data = copy.deepcopy(original_data)
                mutable_data = copy.deepcopy(mutable_data)
                for key in ignored_fields:
                    if key in original_data:
                        del original_data[key]
                    if key in mutable_data:
                        del mutable_data[key]
            changed = not is_equal(original_data, mutable_data)

        return changed

    def get_property(self, name, is_path=False, default=None, original=True,
                     mutated=False):
        """Retrieve model value by field name.

        Retrieve value which is stored in models data storage.

        WARNING: This method should be used internally by module itself.

        :type name:      str
        :param name:     Reference on key/path name for which value should
                         be retrieved.
        :type is_path:   bool
        :param is_path:  Whether provided field name represent key-path or
                         regular field name.
        :param default:  Reference on value which should be used in case
                         if requested field value doesn't exists.
        :type original:  bool
        :param original: Whether original value (from non-mutable version)
                         should be retrieved if possible or not. If set to
                         'False' and received value is 'None' then value
                         will be checked in mutable storage.
        :type mutated:   bool
        :param mutated:  Whether only value from mutable storage is
                         expected or not.

        :return: Stored value or the one which is passed as 'default'.
        """
        value = None
        if original:
            value = super(MutableModel, self).get_property(name,
                                                           is_path=is_path)
        if not original and value is None or mutated:
            value = object_value(self._mutable_data, name, is_path=is_path)

        return value or default

    def set_property(self, name, value=None, is_path=False,
                     create_missing=False, original=False):
        """Update model data in separate storage.

        Changes done in different storage to make it possible to check in
        future whether model information has been changed or not.

        WARNING: This method should be used internally by module itself.

        :type name:            str
        :param name:           Reference on key/path name for which value
                               should be stored.
        :param value:          Reference on object which should be stored or
                               removed (in case if 'None' provided) to/from
                               model.
        :type is_path:         bool
        :param is_path:        Whether provided field name represent
                               key-path or regular field name.
        :type create_missing:  bool
        :param create_missing: Whether missing fields should be created or
                               report thrown an exception.
        :param original:       Whether value should be set to original
                               storage (non-mutable version) or not.
        """
        # Prepare storage for models if required.
        if original and not super(MutableModel, self).initialized:
            super(MutableModel, self).update(dict())
        elif not original and not self.initialized:
            self._mutable_data = dict()
        storage = self._data if original else self._mutable_data
        set_object_value(storage, name, is_path=is_path, value=value,
                         force=create_missing)

    def update(self, data):
        """Update stored model data.

        WARNING: This method should be used internally by module itself.

        :type data:  dict
        :param data: Reference on new information which should be used by
                     model.
        """
        super(MutableModel, self).update(data)
        if self._mutable_data is None:
            self._mutable_data = dict()
        self._mutable_data.update(copy.deepcopy(data or dict()))

    def merge(self):
        """Merge changes in mutable storage with static storage."""
        self._data.update(self._mutable_data)
