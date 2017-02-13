"""Module with set of helper functions"""
import sys
import six


def is_equal(val1, val2):
    """Check whether passed values are equal or not.

    :param val1: First value against which check should be done.
    :param val2: Second value against which check should be done.

    :rtype:  bool
    :return: True in case if passed objects are equal.
    """
    _is_equal = val1 is not None and val2 is not None
    if sys.version_info[0] >= 3:
        if _is_collection(val1) and _is_collection(val2):
            _is_equal = hasattr(val1, 'keys') == hasattr(val2, 'keys')
            _is_equal = _is_equal and len(val1) == len(val2)
            if _is_equal and hasattr(val1, 'keys'):
                for key in val1:
                    _is_equal = key in val2
                    _is_equal = _is_equal and is_equal(val1[key], val2[key])
                    if not _is_equal:
                        break
            elif _is_equal:
                for idx, value in enumerate(val1):
                    _is_equal = is_equal(value, val2[idx])
                    if not _is_equal:
                        break
        elif _is_equal:
            _is_equal = val1 == val2
    elif _is_equal:
        _is_equal = val1 == val2

    if val1 is None and val2 is None:
        _is_equal = True

    return _is_equal


def _is_collection(value):
    """Check whether passed value iterable.

    :param value: Reference on value which should be checked.

    :rtype:  bool
    :return: 'True' in case if passed value represent iterable collection.
    """
    return (isinstance(value, dict) or isinstance(value, list) or
            isinstance(value, tuple))


def object_value(obj, key, is_path=False, default=None):
    """Shortcut to value_for_key and value_for_keypath functions.

    Function allow to handle case when 'dct' is 'None' and can't respond to
    'get()'.
    :param obj:     Reference on object for which value should be
                    retrieved.
    :type key:      str
    :param key:     Reference on string which represent field/key-path
                    under which stored value which should be returned.
    :type is_path:  bool
    :param is_path: Whether 'key' represent field name or key-path.
    :param default: Reference on value which should be returned in case if
                    nothing has been found in object for specified field
                    name.

    :return: Reference on value which is stored for 'key' or 'None' in case
             if dictionary is 'None' or no value for 'key' has been found.
             Default value will be returned if set.
    """
    if not is_path:
        value = value_for_key(obj, key=key, default=default)
    else:
        value = value_for_keypath(obj, keypath=key, default=default)

    return value


def value_for_key(obj, key, default=None):
    """Retrieve value which is stored under specified 'key'.

    Function allow to handle case when 'dct' is 'None' and can't respond to
    'get()'.
    :param obj:     Reference on object for which value should be
                    retrieved.
    :type key:      str
    :param key:     Reference on string which represent field under which
                    stored value which should be returned.
    :param default: Reference on value which should be returned in case if
                    nothing has been found in object for specified field
                    name.

    :raise: IndexError in case if non digit value has been passed as index
            for list container to get value from it.

    :return: Reference on value which is stored for 'key' or 'None' in case
             if dictionary is 'None' or no value for 'key' has been found.
             Default value will be returned if set.
    """
    value = None
    if obj is not None and key is not None:
        if isinstance(obj, dict):
            value = obj.get(key)
        elif isinstance(obj, tuple) or isinstance(obj, list):
            if key.lstrip('-').isdigit():
                index = int(key)
                value = obj[index] if index < len(obj) else None
            else:
                raise IndexError('Unexpected value has been passed as list '
                                 'index: {0}'.format(key))
        else:
            if hasattr(obj, key):
                value = getattr(obj, key)
    if value is None:
        value = default

    return _converted_value(value, default=default)


def value_for_keypath(obj, keypath, default=None):
    """Retrieve value which is stored under specified 'keypath'.

    Function allow to handle case when 'obj' is 'None' and can't respond to
    'get()'.
    :param obj:     Reference on object for which value should be
                    retrieved.
    :type keypath:  str
    :param keypath: Reference on string which represent keypath under which
                    stored value which should be returned.
    :param default: Reference on value which should be returned in case if
                    nothing has been found in object for specified field
                    name.

    :return: Reference on value which is stored for 'key' or 'None' in case
             if dictionary is 'None' or no value for 'key' has been found.
             Default value will be returned if set.
    """
    value = obj
    if value is not None and keypath is not None:
        parts = keypath.split('.')
        for part_idx, part in enumerate(parts):
            value = value_for_key(value, key=part)
            if value is None and part_idx < len(parts) - 1:
                break
    if value is None:
        value = default

    return _converted_value(value, default=default)


def set_object_value(obj, key, is_path=False, value=None, force=False):
    """Shortcut to set_value_for_key and set_value_for_keypath functions.

    Function allow to handle case when 'obj' is 'None' or doesn't have
    setters (if not collection then 'hasattr' will be used to check whether
    value can be set).
    :param obj:     Reference on object which should be updated with new
                    value.
    :type key:      str
    :param key:     Reference on string which represent field/key-path
                    under which stored value which should be returned.
    :type is_path:  bool
    :param is_path: Whether 'key' represent field name or key-path.
    :param value:   Reference on object which should be added to object. If
                    value is 'None' then it will be deleted from specified
                    location.
    :type force:    bool
    :param force:   Whether new entry should be added at the end of array
                    if index out of bound. If index is inside of array
                    range with value set to 'True' value will be inserted
                    at specified index instead of replace. If one of
                    key-path components refer to non-existing collection it
                    can be created if value is set to 'True'.

    :raise: IndexError in case if non digit value has been passed as index
            for list container to get value from it.
    :raise: TypeError in case if according to keypath tuple should be
            modified.
    :raise: AttributeError in case if there was an attempt to set value
            using setattr to object which doesn't have such attribute
            (force) or attribute is read-only.
    :raise: KeyError in case if value destination or intermediate
            collections doesn't exist and 'force' flag didn't set to 'True'
            to allow intuitive objects creation along keypath.
    """
    if not is_path:
        set_value_for_key(obj, key=key, value=value, force=force)
    else:
        set_value_for_keypath(obj, keypath=key, value=value, force=force)


def set_value_for_key(obj, key, value=None, force=False):
    """Update value which is stored inside of collection.

    Function allow to handle case when 'obj' is 'None' or doesn't have
    setters (if not collection then 'hasattr' will be used to check whether
    value can be set).
    :param obj:   Reference on object which should be updated with new
                  value.
    :type key:    str
    :param key:   Reference on key/index under which 'value' should be
                  stored.
    :param value: Reference on object which should be added to object. If
                  value is 'None' then it will be deleted from specified
                  location.
    :type force:  bool
    :param force: Whether set should be forced against non-collection
                  object (using 'setattr') or whether new entry should be
                  added at the end of array if index out of bound. If index
                  is inside of array range with value set to 'True' value
                  will be inserted at specified index instead of replace.

    :raise: IndexError in case if non digit value has been passed as index
            for list container to get value from it.
    :raise: TypeError in case if according to keypath tuple should be
            modified.
    :raise: AttributeError in case if there was an attempt to set value
            using setattr to object which doesn't have such attribute
            (force) or attribute is read-only.
    """
    if obj is not None and value is None:
        if key is not None:
            _delete_value_for_key(obj, key)
    if isinstance(obj, dict):
        obj[key] = value
    elif isinstance(obj, list):
        if not key.lstrip('-').isdigit():
            raise IndexError('Unexpected value has been passed as list index: '
                             '{0}'.format(key))
        index = int(key)
        if index < len(obj):
            if not force:
                obj[index] = value
            else:
                obj.insert(index, value)
        elif force and value is not None:
            obj.append(value)
    elif isinstance(obj, tuple):
        raise TypeError('\'tuple\' is immutable and can\'t modify value at: '
                        '{0}'.format(key))
    elif obj is not None and (hasattr(obj, key) or force):
        setattr(obj, key, value)


def _delete_value_for_key(obj, key):
    """Remove value for specified key from object.

    :param obj: Reference on object from which value should be removed.
    :type key:  str
    :param key: Reference on name of field / index for which value should
                be removed from object.

    :raise: TypeError in case if according to keypath tuple should be
            modified.

    """
    if isinstance(obj, dict):
        if key in obj:
            del obj[key]
    elif isinstance(obj, list):
        index = int(key)
        if index < len(obj):
            del obj[index]
    elif isinstance(obj, tuple):
        raise TypeError('\'tuple\' is immutable and can\'t modify value at '
                        '{0} index'.format(key))
    elif hasattr(obj, key):
        delattr(obj, key)


def set_value_for_keypath(obj, keypath, value=None, force=False):
    """Update value which is stored inside of collection.

    Function allow to handle case when 'obj' is 'None' or doesn't have
    setters (if not collection then 'hasattr' will be used to check whether
    value can be set).
    :param obj:     Reference on object which should be updated with new
                    value.
    :type keypath:  str
    :param keypath: Reference on key-path under which 'value' should be
                    stored.
    :param value:   Reference on object which should be added to object. If
                    value is 'None' then it will be deleted from specified
                    location.
    :type force:    bool
    :param force:   Whether new entry should be added at the end of array
                    if index out of bound. If index is inside of array
                    range with value set to 'True' value will be inserted
                    at specified index instead of replace. If one of
                    key-path components refer to non-existing collection it
                    can be created if value is set to 'True'.

    :raise: KeyError in case if value destination or intermediate
            collections doesn't exist and 'force' flag didn't set to 'True'
            to allow intuitive objects creation along keypath.
    """
    if obj is not None and keypath is not None:
        parts = keypath.split('.')
        if len(parts) == 1:
            set_value_for_key(obj, keypath, value=value, force=force)
        elif len(parts) > 1:
            container_path = '.'.join(parts[:-1])
            container = value_for_keypath(obj, container_path)
            if container is None and force:
                _create_iterable_for_keypath(obj, keypath)
                container = value_for_keypath(obj, container_path)
            if container is None:
                raise KeyError('One of iterable objects in key-path doesn\'t '
                               'exists. Set force=True if not existing '
                               'entries should be created following key-path.')
            set_value_for_key(container, parts[-1], value=value, force=force)


def _create_iterable_for_keypath(obj, keypath):
    """Create required objects along specified keypath.

    This function help setter for key-path to prepare target collection
    where passed value should be stored.
    :param obj:     Reference on object inside of which required structure
                    should be created.
    :type keypath:  str
    :param keypath: Reference on keypath which should be used as template
                    for new 'obj' structure.

    :raise: IndexError in case if non digit value has been passed as index
            for list container to get value from it.
    :raise: KeyError in case if there is value at keypath but it's type
            doesn't allow to modify it (for instance if string appeared in
            the middle of following along key-path and because it is not
            collection it will fail).
    """
    container = obj
    c_value = obj
    parts = keypath.split('.')
    parts_len = len(parts)

    for part_idx, part in enumerate(parts):
        # Only integer values allowed as index for list container.
        if isinstance(container, list) and not part.lstrip('-').isdigit():
            path = '.'.join(parts[:part_idx + 1])
            raise IndexError('Unexpected index (\'{0}\') for '.format(part) +
                             '\'list\' at \'{0}\'.'.format(path))

        # Check what kind of data represent current value basing on next
        # key type. If next key will be digit then current value
        # potentially is 'list'. It is possible what current value is
        # 'dict' but it is best what function can guess. To ensure what
        # type should be, make sure what objects exist exists before value
        #  is set using key-path.
        val_is_iterable = False
        val_is_list = False
        if part_idx + 1 < parts_len:
            next_part = parts[part_idx + 1].lstrip('-')
            val_is_list = next_part.isdigit()
            val_is_iterable = True

        c_value = value_for_key(c_value, key=part)
        if c_value is None and part_idx < parts_len - 1:
            if val_is_iterable:
                c_value = list() if val_is_list else dict()
            if c_value is not None:
                set_value_for_key(container, part, value=c_value, force=True)

        if c_value is not None:
            if _is_collection(c_value):
                container = c_value
            elif part_idx < parts_len - 1:
                expected_type = 'list' if val_is_list else 'dict'
                path = '.'.join(parts[:part_idx + 1])
                cls = IndexError if val_is_list else KeyError
                raise cls('Unexpected object found at: \'{0}\' '.format(path) +
                          'where {0} is expected.'.format(expected_type))


def _converted_value(value, default):
    """Convert value to type of 'default' value.

    If 'default' value has been provided, then it is expected what original
    value is expected to be same type.
    :param value:   Reference on original value which should be converted
                    if required.
    :param default: Reference on value which type should be used for proper
                    'value' conversion.

    :return:  Converted 'value'.
    """
    if value is not None and default is not None:
        if isinstance(default, six.string_types):
            return str(value)
        elif isinstance(default, six.integer_types):
            return int(value)

    return value
