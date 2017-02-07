from request import Request

class ListingRequest(Request, object):
  def __init__(self, client, query={}):
    return super(ListingRequest, self).__init__(client, 'get', client.getURL('listings'), query)
