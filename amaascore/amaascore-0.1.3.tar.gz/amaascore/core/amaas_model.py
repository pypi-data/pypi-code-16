import datetime
from decimal import Decimal
import json


def json_handler(value):
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        return (datetime.datetime.min + value).time().isoformat()
    if isinstance(value, set):
        return list(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, AMaaSModel):
        return value.to_json()
    raise TypeError("JSON Handler Failed on value '%s': Unknown type '%s'" % (value, type(value)))


def to_json(dict_to_convert):
    return json.loads(to_json_string(dict_to_convert))


def to_json_string(dict_to_convert):
    return json.dumps(dict_to_convert, ensure_ascii=False, default=json_handler, indent=4, separators=(',', ': '))


class AMaaSModel(object):

    @staticmethod
    def non_interface_attributes():
        """ Potentially convert this to attribute annotations """
        return []

    @staticmethod
    def amaas_model_attributes():
        return ['created_by', 'updated_by', 'created_time', 'updated_time', 'version']

    def __init__(self, *args, **kwargs):
        self.version = kwargs.get('version') or 1
        self.created_by = kwargs.get('created_by') or 'TEMP'  # Should come from logged in user
        self.updated_by = kwargs.get('updated_by') or 'TEMP'  # Should come from logged in user
        self.created_time = kwargs.get('created_time')  # Comes from database
        self.updated_time = kwargs.get('updated_time')  # Comes from database

    def to_interface(self):
        """
        Returns only the JSON attributes required when interfacing with the AMaaS Core services.
        Non-interface attributes are popped out.
        :return:
        """
        dict_to_convert = self.__dict__
        [dict_to_convert.pop(attr) for attr in self.non_interface_attributes()]
        return self.to_json(dict_to_convert)

    def to_json(self, dict_to_convert=None):
        dict_to_convert = dict_to_convert or self.__dict__
        # Convert internal property values (_XYZ) to the correctly named one (XYZ)
        # Is there a better way of doing this instead of relying on the first character?
        mapped_dict = {}
        for key, value in dict_to_convert.items():
            key = key[1:] if key[0] == '_' else key
            mapped_dict[key] = value
        return to_json(mapped_dict)

    def __repr__(self):
        """
        # TODO - check the nested dictionaries
        :return:
        """
        return str(self.__dict__)

    def __eq__(self, other):
        """Override the default Equals behavior"""
        if isinstance(other, self.__class__):
            my_dict = self.__dict__
            other_dict = other.__dict__
            # Strip out the database generated fields:
            [my_dict.pop(attr, None) for attr in self.amaas_model_attributes()]
            [other_dict.pop(attr, None) for attr in self.amaas_model_attributes()]
            return my_dict == other_dict
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return not self.__eq__(other)
        return NotImplemented

    def __hash__(self):
        """Override the default hash behavior (that returns the id or the object)"""
        output = []
        for (key, value) in self.__dict__.items():
            output_value = hash(tuple(sorted(value))) if isinstance(value, dict) else value
            output.append((key, output_value))
        return hash(tuple(sorted(output)))

