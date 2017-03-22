import os

from bitfusion.api.base import BaseMixin, UpdateableMixin, HealthMixin
from bitfusion.api import Gpu
from bitfusion.lib import API

class Node(BaseMixin, UpdateableMixin, HealthMixin):
  base_url = '/node'

  def __str__(self):
    output = '\nNode {id} @ {ip} - {name} - {mem} MB Memory - {type}'

    output = output.format(id=self.data['id'],
                           ip=self.data['ip_address'],
                           name=self.data.get('name', 'unnamed'),
                           mem=self.data['memory'],
                           type=self.data['type'].upper())

    for g in self.data.get('gpus', []):
      gpu = Gpu(g)
      output += '\n\t' + str(gpu)

    return output + '\n'


  def activate(self):
    self.load(API.post(os.path.join(self.base_url, str(self.id), 'activate')))


  def deactivate(self):
    self.load(API.post(os.path.join(self.base_url, str(self.id), 'deactivate')))


  @classmethod
  def add_by_ip(cls, ip):
    return API.post(os.path.join(cls.base_url, 'add', ip))
