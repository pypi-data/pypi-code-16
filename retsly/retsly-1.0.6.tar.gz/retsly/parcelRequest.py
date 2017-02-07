from request import Request

class ParcelRequest(Request, object):
  def __init__(self, client, query={}):
    return super(ParcelRequest, self).__init__(client, 'get', client.getURL('parcels'), query)
