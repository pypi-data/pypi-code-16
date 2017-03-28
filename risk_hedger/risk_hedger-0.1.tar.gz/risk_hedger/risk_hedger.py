"""low level SliceMatrix-IO API client"""

API_STAGE = "beta"

import pandas as pd
import numpy as np
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json

region_api_map    = {"us-east-1": "5dxh2p2yjh"}

class HedgeIO():
  def __init__(self, api_key, region = "us-east-1"):
    self.api_key  = api_key
    self.region   = region
    self.api      = region_api_map[region]

  def get_ratio(self, base, hedge):
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/ratio'
    url += "?base=" + base
    url += "&hedge=" + hedge
    headers = {'x-api-key': self.api_key, 
               'Content-Type': 'application/json'}
    r = requests.get(url, verify = False, headers = headers)
    return json.loads(r.text)
  
  def get_hedges(self, base):
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/hedges'
    url += "?base=" + base
    headers = {'x-api-key': self.api_key,
               'Content-Type': 'application/json'}
    r = requests.get(url, verify = False, headers = headers)
    try:
        return pd.DataFrame(json.loads(r.text)).sort_values(by="hedges")
    except:
        return json.loads(r.text)

  def get_symbols(self):
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/symbols'
    headers = {'x-api-key': self.api_key,
               'Content-Type': 'application/json'}
    r = requests.get(url, verify = False, headers = headers)
    try:
        return pd.DataFrame(json.loads(r.text))
    except:
        return json.loads(r.text)

