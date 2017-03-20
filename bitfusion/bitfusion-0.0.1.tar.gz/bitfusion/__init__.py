from bitfusion import api
from bitfusion.lib import http_api

class BFApi():
  def __init__(self, host_url='http://localhost:5000', base_path=''):
    http_api.HTTP_HOST = host_url
    http_api.BASE_PATH = base_path

    self.Gpu = api.Gpu
    self.Node = api.Node
    self.Volume = api.Volume
    self.Workspace = api.Workspace
