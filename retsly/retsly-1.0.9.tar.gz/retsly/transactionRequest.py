from request import Request

class TransactionRequest(Request, object):
  def __init__(self, client, query={}):
    return super(TransactionRequest, self).__init__(client, 'get', client.getURL('transactions'), query)
