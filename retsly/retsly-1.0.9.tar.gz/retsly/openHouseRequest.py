from request import Request

class OpenHouseRequest(Request, object):
  def __init__(self, client, query={}):
    return super(OpenHouseRequest, self).__init__(client, 'get', client.getURL('openhouses'), query)
