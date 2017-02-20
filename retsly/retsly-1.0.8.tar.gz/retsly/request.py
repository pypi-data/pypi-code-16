import requests
import jsonurl

class Request:
  def __init__(self, client, method, url, query=None):
    """
    Construct request for the Retsly API

    Args:
      client (dict):          Retsly client
      method (string):        method
      url (string):           url
      query (list):           query

    """
    self.client = client
    self.method = method
    self.url = url
    self.query = query if query is not None else {}


  def query(self, query={}):
    self.query.update(query);
    return self;

  def where(self, key, op=None, value=None):
    if (op is None and value is None):
      if isinstance(key, basestring):
        array = key.split(' ')
      elif isinstance(key, list):
        array = key

      if len(array) == 2:
        key, op, value = array[0], 'eq', array[1]
      elif len(array) == 3:
        key, op, value = array[0], array[1], array[2]
      else:
          raise ValueError('Please provide a valid query parameter')
    # assume operator is eq if only two arguments is provided
    elif (value is None):
      value = op
      op = 'eq'

    op = getOperator(op)

    if op == 'eq':
      query = {key: value}
    else:
      query = {key: {op: value}}

    self.query.update(query)
    return self

  def limit(self, value=None):
    if value is not None: self.query.update({'limit': value})
    return self

  def offset(self, value=None):
    if value is not None: self.query.update({'offset': value})
    return self

  def nextPage(self):
    if 'limit' in self.query:
      offset = self.query['offset'] if 'offset' in self.query else 0
      self.query['offset'] = offset + self.query['limit']
    return self

  def prevPage(self):
    if 'limit' in self.query and 'offset' in self.query:
      l = self.query['offset'] - self.query['limit']
      self.query['offset'] = l if l > 0 else 0
    return self

  def get(self, id):
    self.method = 'get'
    return self.end(id)

  def getAll(self):
    self.method = 'get'
    return self.end()

  def encodeQS(self):
    return jsonurl.query_string(self.query).replace('..', '.')

  def getURL(self, id):
    key = '/' + id if (id is not None) else ''
    return self.url + key + '?' + self.encodeQS()

  def end(self, id=None):
    if self.client.token: headers = {'Authorization': 'Bearer '+self.client.token}
    else: headers = {}
    r = requests.get(self.getURL(id), headers=headers);
    return r.json()

def getOperator(op):
  if op == '<' or op == 'lt': return 'lt'
  elif op == '>' or op == 'gt': return 'gt'
  elif op == '<=' or op == 'lte': return 'lte'
  elif op == '>=' or op == 'gte': return 'gte'
  elif op == '!=' or op == 'ne': return 'ne'
  elif op == '=' or op == 'eq': return 'eq'
  elif op == 'regex': return 'regex'
  else: raise ValueError('You must provide a valid operator')
