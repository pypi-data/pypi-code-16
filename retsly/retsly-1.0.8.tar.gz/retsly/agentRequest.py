from request import Request

class AgentRequest(Request, object):
  def __init__(self, client, query={}):
    return super(AgentRequest, self).__init__(client, 'get', client.getURL('agents'), query)
