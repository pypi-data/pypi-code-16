import platform
import requests
from .config import connection_retries
from .config import connection_timeout
from requests.adapters import HTTPAdapter

_session = None

def __return_wrapper(resp):
    if resp.status_code != 200 or resp.headers.get('X-Reqid') is None:
        return None, ResponseInfo(resp)
    ret = resp.json() if resp.text != '' else{}
    return ret, ResponseInfo(resp)


def _init():
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=connection_retries))
    global _session
    _session = session


def _post(url, headers, data=None, files=None):
    null =''
    true= 'true'
    false='false'
    if _session is None:
        _init()
    try:
        r = _session.post(url=url, data=data, files=files, headers=headers, timeout=connection_timeout, verify=False)
    except Exception as e:
        return None, ResponseInfo(None, e)
    return __return_wrapper(r)


def _get(url, headers=None,data=None):
    null =''
    true= 'true'
    false='false'
    try:
        r = requests.get(url, data=data,timeout=connection_timeout, headers=headers, verify=False)
    except Exception as e:
        return -1,e
    return r.status_code, eval(str(r.text))

class ResponseInfo(object):

    def __init__(self, response, exception=None):
        self.__response = response
        self.exception = exception
        if response is None:
            self.status_code = -1
            self.text_body = None
            self.req_id = None
            self.x_log = None
            self.error = str(exception)
        else:
            self.status_code = response.status_code
            self.text_body = response.text
            self.req_id = response.headers.get('X-Reqid')
            self.x_log = response.headers.get('X-Log')
            if self.status_code >= 400:
                ret = response.json() if response.text != '' else None
                if ret is None or ret['error'] is None:
                    self.error = 'unknown'
                else:
                    self.error = ret['error']
            if self.req_id is None and self.status_code == 200:
                self.error = 'server is not qiniu'

    def ok(self):
        return self.status_code == 200 and self.req_id is not None

    def need_retry(self):
        if self.__response is None or self.req_id is None:
            return True
        code = self.status_code
        if (code // 100 == 5 and code != 579) or code == 996:
            return True
        return False

    def connect_failed(self):
        return self.__response is None or self.req_id is None

    def __str__(self):
        return ', '.join(['%s:%s' % item for item in self.__dict__.items()])

    def __repr__(self):
        return self.__str__()
