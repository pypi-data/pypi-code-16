import sys
import os

import requests

HTTP_HOST = None
BASE_PATH = None

TIMEOUT=10

class ApiRequest(requests.Session):
  def get(self, suffix):
    try:
      res = super(ApiRequest, self).get(self._build_url(suffix), timeout=TIMEOUT)
    except Exception as e:
      return self._handle_request_error(e)

    return self._handle_response(res)


  def post(self, suffix, data=None):
    try:
      res = super(ApiRequest, self).post(self._build_url(suffix), json=data, timeout=TIMEOUT)
    except Exception as e:
      return self._handle_request_error(e)

    return self._handle_response(res)


  def put(self, suffix, data):
    try:
      res = super(ApiRequest, self).put(self._build_url(suffix), json=data, timeout=TIMEOUT)
    except Exception as e:
      return self._handle_request_error(e)

    return self._handle_response(res)
  

  def delete(self, suffix):
    try:
      res = super(ApiRequest, self).delete(self._build_url(suffix), timeout=TIMEOUT)
    except Exception as e:
      return self._handle_request_error(e)

    return self._handle_response(res)

  @staticmethod
  def _build_url(suffix):
    return HTTP_HOST + os.path.join(BASE_PATH, suffix)

  def _handle_response(self, res):
    try:
      res.raise_for_status()
    except requests.exceptions.HTTPError as e:
      print(e)
      sys.exit(1)

    return res.json()


  def _handle_request_error(self, e):
    raise Exception({ 'errors': str(e) })

API = ApiRequest()

