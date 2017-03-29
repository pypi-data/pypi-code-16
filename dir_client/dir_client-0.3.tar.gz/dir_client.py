import hashlib
import base64
import httplib
import urllib
import time
from threading import Timer

def generate_hmac(secret, content):
  return base64.b64encode(hashlib.sha224(secret + content).digest())

class Client():
  def __init__(self, api_key, secret, service, host, port=80):
    self.service = service
    self.api_key = api_key
    self.secret = secret
    self.host = host
    self.port = port
    self.timer = None

  def request(self, method, path, query_params = {}):
    timestamp = str(int(time.time()))
    method = str.upper(method)
    query_params['api_key'] = self.api_key
    query_params['timestamp'] = timestamp
    url = urllib.quote(path) + '?' + urllib.urlencode(query_params)

    hmac = generate_hmac(self.secret, method + url)

    try:
      conn = httplib.HTTPConnection(self.host,self.port)

      conn.request(method, url, '', {'Authorization': hmac})
      resp = conn.getresponse()
      resp_body = resp.read()
      resp_status = resp.status

      conn.close()
    except httplib.HTTPException as e:
      raise

    if resp_status < 200 or resp_status >= 300:
      raise Exception('Service directory server responded with non 2xx status: '+resp_body)

    return resp_body

  def auto_renew(self, server, ttl=30, period=-5):
    if period<=0:
      period = ttl + period
    if self.timer:
      self.timer.cancel()
    self.disable_timer = False

    def renew():
      self.reg_server(server, ttl)
      self.timer = Timer(period, renew)
      if not self.disable_timer:
        self.timer.start()

    renew()

  def reg_server(self, server, ttl=30):
    self.request('PUT','/server/'+self.service+'/'+server, {'ttl':str(ttl)})

  def dereg_server(self, server):
    self.disable_timer = True
    if self.timer:
      self.timer.cancel()
    self.timer = None

    self.request('DELETE','/server/'+self.service+'/'+server)

  def reg_service(self, start_command):
    self.request('PUT','/register/'+self.service, {'start':str(start_command)})
