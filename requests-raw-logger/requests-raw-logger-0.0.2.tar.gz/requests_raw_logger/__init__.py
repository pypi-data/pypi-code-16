import time

import requests


class HTTPLog(object):
    def __init__(self):
        self._request = None
        self._response = None
        self.response_time = None

    def set_request(self, request):
        self._request = {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'body': request.body or ''
        }

    def set_response(self, response):
        self._response = {
            'status_code': response.status_code,
            'reason': response.reason,
            'headers': dict(response.headers),
            'body': response.content or '',
        }

    def set_response_time(self, response_time):
        self.response_time = response_time

    @property
    def request(self):
        return '{} {}\n{}\n\n{}'.format(
            self._request['method'],
            self._request['url'],
            '\n'.join('{}: {}'.format(k, v)
                      for k, v in self._request['headers'].items()),
            self._request['body'])

    @property
    def response(self):
        return '{} {}\n{}\n\n{}'.format(
            self._response['status_code'],
            self._response['reason'],
            '\n'.join('{}: {}'.format(k, v)
                      for k, v in self._response['headers'].items()),
            self._response['body'])


class LoggerAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        super(LoggerAdapter, self).__init__(*args, **kwargs)
        self.logs = []

    def send(self, request, *args, **kwargs):
        log = HTTPLog()
        self.logs.append(log)

        log.set_request(request)
        start = time.time()
        resp = super(LoggerAdapter, self).send(request, *args, **kwargs)
        response_time = time.time() - start
        log.set_response(resp)
        log.set_response_time(response_time)
        return resp


class RequestsLogger(object):
    def __init__(self):
        self.logs = []
        self._adapter = LoggerAdapter()
        self.logs = self._adapter.logs

    def register(self, session):
        session.mount('http://', self._adapter)
        session.mount('https://', self._adapter)

    @property
    def total_response_time(self):
        return sum([i.response_time for i in self._adapter.logs])

    @property
    def requests(self, separator='##################################'):
        req_logs = ['({}){}'.format(i + 1, j.request)
                    for i, j in enumerate(self._adapter.logs)]
        return '\n\n{}\n\n'.format(separator).join(req_logs)

    @property
    def responses(self, separator='##################################'):
        res_logs = ['({}){}'.format(i + 1, j.response)
                    for i, j in enumerate(self._adapter.logs)]
        return '\n\n{}\n\n'.format(separator).join(res_logs)
