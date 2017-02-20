from request import Request

class AssessmentRequest(Request, object):
  def __init__(self, client, query={}):
    return super(AssessmentRequest, self).__init__(client, 'get', client.getURL('assessments'), query)
