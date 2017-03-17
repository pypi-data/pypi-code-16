import requests

domain = 'http://localhost'

def call(endpointToken, parameters):
  r = requests.post(domain, json = {'endpointToken':endpointToken, 'parameters':parameters})
  return r.json()

def setDomain(dom):
  global domain
  domain = dom
