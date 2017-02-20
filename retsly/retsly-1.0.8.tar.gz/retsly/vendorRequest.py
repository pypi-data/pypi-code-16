from request import Request

class VendorRequest(Request, object):
  def __init__(self, client, query={}):
    return super(VendorRequest, self).__init__(client, 'get', client.getURL('vendors'), query)
