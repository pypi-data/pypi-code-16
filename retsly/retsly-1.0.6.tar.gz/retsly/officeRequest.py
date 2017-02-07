from request import Request

class OfficeRequest(Request, object):
  def __init__(self, client, query={}):
    return super(OfficeRequest, self).__init__(client, 'get', client.getURL('offices'), query)
