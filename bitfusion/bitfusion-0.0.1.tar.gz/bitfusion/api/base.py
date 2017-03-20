import os

from bitfusion.lib import API

class BaseMixin():
  def __init__(self, data=None):
    if data:
      self.load(data)


  def load(self, api_data):
    self.id = api_data.get('id')
    self.data = api_data


  def reload(self):
    if not self.id:
      raise Exception('Cannot reload without an ID')

    self.load(self.get_data_by_id(self.id))


  def save(self):
    res = API.post(self.base_url, self.data)
    self.load(res)

  
  def delete(self):
    return API.delete(os.path.join(self.base_url, str(self.id)))


  @classmethod
  def get(cls, data_id):
    return cls(cls.get_data_by_id(data_id))


  @classmethod
  def get_all(cls):
    raw_data = API.get(cls.base_url)
    instance_list = []
    
    for d in raw_data:
      instance_list.append(cls(d))

    return instance_list


  @classmethod
  def get_data_by_id(cls, data_id):
    return API.get(os.path.join(cls.base_url, str(data_id)))


class CreatableMixin():
  @classmethod
  def create(cls, **kwargs):
    return API.post(cls.base_url, kwargs)
