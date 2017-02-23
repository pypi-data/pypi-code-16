import platform
import requests
from .config import connection_retries
from .config import connection_timeout
from requests.adapters import HTTPAdapter

_session = None

def __return_wrapper(resp):
    if resp.status_code != 200 or resp.headers.get('X-Reqid') is None:
        return None, ResponseInfo(resp)


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
        return -1,e
    return r.status_code, eval(str(r.text))


def _get(url, headers=None,data=None):
    null =''
    true= 'true'
    false='false'
    try:
        r = requests.get(url, data=data,timeout=connection_timeout, headers=headers, verify=False)
    except Exception as e:
        return -1,e
    return r.status_code, eval(str(r.text))


