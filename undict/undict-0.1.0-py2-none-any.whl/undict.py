from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


def _undict_impl(json_obj):
  if isinstance(json_obj, dict):
    return UndictWrapper(json_obj)
  elif isinstance(json_obj, list):
    return [_undict_impl(item) for item in json_obj]
  return json_obj
  

class UndictWrapper(object):
  def __init__(self, data):
    assert isinstance(data, dict)
    self.__data_dict = {}
    for k, v in data.items():
      self.__data_dict[k] = _undict_impl(v)

  def __getattr__(self, field):
    if field not in self.__data_dict:
      raise KeyError(field)
    return self.__data_dict[field]

  def __setattr__(self, field, data):
    if field.startswith('_UndictWrapper__'):
      return super.__setattr__(self, field, data)

    if isinstance(data, dict):
      data = _undict_impl(data)
    self.__data_dict[field] = data
  
  '''
  Class methods. Every class method will violate the easy usage pattern. For exmaple, 
  if we have a method call **get**, that means obj.get will be different from obj['get'].
  To minimize the number of method needed, we only expose one single API to return the underlying
  dict.
  '''
  def to_dict(self):
    return self.__data_dict


def undict(json_obj):
  return _undict_impl(json_obj)
