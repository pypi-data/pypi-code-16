# noinspection PyCallByClass
from expection import SerialiserMapError
from versioning import Versioning


class Serializer(object):
    """
    get required json in single line call as below
    data = Serializer(instance).required_json
    """
    DEEP_LEVEL_KEY_SEPARATOR = '__'

    BODY_MAP = dict()

    REDUCER = None

    MODULE = None

    def __init__(self, instance):
        if not self.BODY_MAP:
            raise NotImplementedError('Missing BODY_MAP')
        if not self.REDUCER or not callable(self.REDUCER):
            raise NotImplementedError('Missing REDUCER')

        self.instance = instance
        self.data = dict()

    def _get_custom_obj_handler(self, obj_handler_key):
        reducer_func = getattr(self, '_obj_handler__%s' % obj_handler_key, None)
        if not callable(reducer_func):
            raise NotImplementedError('Missing "%s" Custom Object Handler' % obj_handler_key)
        return reducer_func

    def _obj_handler__self(self, key, obj, value_type):
        obj = self
        if not hasattr(obj, key):
            raise NotImplementedError('Missing or Incorrect "%s" Custom Property' % key)
        response = getattr(obj, key)
        return value_type(response) if not response == None else None

    def _obj_handler__default(self, key, obj, value_type):
        default_map = {
            'None': None,
            'dict': dict(),
            'list': list(),
            'True': True,
            'False': False,
        }
        response = key if key not in default_map else default_map[key]
        return value_type(response) if value_type else response

    def _obj_handler__child(self, key, obj, value_type):
        serialiser = self._str_to_class(key.split(self.DEEP_LEVEL_KEY_SEPARATOR)[0])
        key = self.DEEP_LEVEL_KEY_SEPARATOR.join(key.split(self.DEEP_LEVEL_KEY_SEPARATOR)[1:])
        child_obj = obj[key]
        if value_type == list:
            response = [serialiser(o).required_json for o in child_obj]
        else:
            response = serialiser(child_obj[0] if isinstance(child_obj, list) else child_obj).required_json
        return response

    def _obj_handler(self, key, obj, value_type):
        response = reduce(self.REDUCER, key.split(self.DEEP_LEVEL_KEY_SEPARATOR), obj)
        return value_type(response) if not response == None else None

    def _get_required_value(self, value_info, obj):
        data_key = value_info[0]
        value_type = value_info[1]
        value_required = value_info[3] if len(value_info) > 3 else True

        if data_key.startswith(self.DEEP_LEVEL_KEY_SEPARATOR):
            obj_handler_key = data_key.split(self.DEEP_LEVEL_KEY_SEPARATOR)[1]
            data_key = data_key[len('__%s__' % obj_handler_key):]
            obj_handler_func = self._get_custom_obj_handler(obj_handler_key)
        else:
            obj_handler_func = self._obj_handler

        try:
            return obj_handler_func(data_key, obj, value_type)
        except KeyError as e:
            if not value_required:
                return value_info[2]
            else:
                raise SerialiserMapError(value_info)

    def _get_value(self, value):
        value_by_type_map = {
            tuple: lambda x: self._get_required_value(x, self.instance),
            dict: lambda x: {k: self._get_value(v) for k, v in x.items()},
        }
        get_value = lambda x: value_by_type_map[type(x)](x)
        response = get_value(value)

        if not response == None:
            return response
        else:
            return value[2] if len(value) > 2 else None

    def _str_to_class(self, class_name):
        if not self.MODULE:
            raise NotImplementedError('Missing MODULE to get Child Serialiser Class')
        try:
            klass = getattr(self.MODULE, class_name)
        except AttributeError:
            raise NotImplementedError('Missing Serialiser Type "%s" Class' % class_name)
        return klass

    @property
    def required_json(self):
        return {required_key: self._get_value(required_value_info)
                for required_key, required_value_info in self.BODY_MAP.items()}


class VersionedSerializer(Versioning, Serializer):
    """
    get required json in single line call as below
    data = VersionedSerializer(instance, version).required_json
    """

    def __init__(self, instance, version):
        Versioning.__init__(self, version)
        Serializer.__init__(self, instance)
