import json
import requests
import multiprocessing

import mprequest.util as util

_HTTP_GET_METHOD = 'GET'
_HTTP_DELETE_METHOD = 'DELETE'
_HTTP_PUT_METHOD = 'PUT'
_HTTP_POST_METHOD = 'POST'


class ResponseException(Exception):
    def __init__(self, msg, body=None):
        self.msg = msg
        self.body = body

    def __str__(self):
        return self.msg


class RequesterException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg


class RequestBatch(object):
    def __init__(self):
        self.requests = list()

    def prepare_get(self, url, ctx=None, **kwargs):
        self.requests.append(
            Request.prepare_get(url, ctx, **kwargs))

    def prepare_delete(self, url, ctx=None, **kwargs):
        self.requests.append(
            Request.prepare_delete(url, ctx, **kwargs))

    def prepare_put(self, url, ctx=None, **kwargs):
        self.requests.append(
            Request.prepare_put(url, ctx, **kwargs))

    def prepare_post(self, url, ctx=None, **kwargs):
        self.requests.append(
            RequestBatch.prepare_post(url, ctx, **kwargs))


class Response(object):
    def __init__(self, status_code, body, ctx):
        self.status_code = status_code
        self.body = body
        self.ctx = ctx

    def raise_on_non_success(self):
        self.raise_on(lambda sc: sc < 200 or sc >= 300)

    def raise_on(self, decider):
        if decider(self.status_code):
            raise ResponseException('Bad response status: {}'.format(self.status_code), self.body)

    def json(self):
        return json.loads(self.body)


class RequestResult(object):
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error

    @property
    def successful(self):
        return self.error is None


class Request(object):
    def __init__(self, url, method, ctx, **kwargs):
        self._url = url
        self._method = method
        self._ctx = ctx
        self._kwargs = kwargs

        self._check_kwargs()

    def _check_kwargs(self):
        if 'files' in self._kwargs:
            for v in self._kwargs['files'].values():
                if not isinstance(v, str):
                    raise RequesterException('When uploading files specify filenames, not file objects.')

    def _make_request(self, session):
        session_func = None
        if self._method == _HTTP_GET_METHOD:
            session_func = session.get
        elif self._method == _HTTP_PUT_METHOD:
            session_func = session.put
        elif self._method == _HTTP_POST_METHOD:
            session_func = session.post
        elif self._method == _HTTP_DELETE_METHOD:
            session_func = session.delete
        else:
            raise RequesterException('Method {} not supported!'.format(self.method))

        # Copy the kwargs dict
        kwargs = self._kwargs.copy()

        # If files were specified, open them here
        if 'files' in kwargs:
            real_files = dict()
            for k, path in kwargs['files'].items():
                real_files[k] = open(path, 'rb')
            kwargs['files'] = real_files

        return session_func(
            url=self._url,
            **kwargs)

    def do(self, session):
        result = None

        try:
            raw_response = self._make_request(session)
            result = RequestResult(
                response=Response(raw_response.status_code, raw_response.text, self._ctx))
            raw_response.close()
        except Exception as ex:
            result = RequestResult(
                error=ex)

        return result

    @classmethod
    def prepare_get(cls, url, ctx=None, **kwargs):
        return Request(url, _HTTP_GET_METHOD, ctx, **kwargs)

    @classmethod
    def prepare_delete(cls, url, ctx=None, **kwargs):
        return Request(url, _HTTP_DELETE_METHOD, ctx, **kwargs)

    @classmethod
    def prepare_put(cls, url, ctx=None, **kwargs):
        return Request(url, _HTTP_PUT_METHOD, ctx, **kwargs)

    @classmethod
    def prepare_post(cls, url, ctx=None, **kwargs):
        return Request(url, _HTTP_POST_METHOD, ctx, **kwargs)


class RequesterPool(object):
    def __init__(self, num_workers=None, **session_args):
        if num_workers is None:
            num_workers = multiprocessing.cpu_count() * 2

        self._worker_pool = multiprocessing.Pool(
            processes=num_workers,
            initializer=Requester.init_session,
            initargs=(session_args,))

    def do(self, request):
        result = self._worker_pool.map(Requester.do, [request])[0]
        if result.successful is False:
            raise result.error
        return result.response

    def batch(self, batch):
        if type(batch) is not RequestBatch:
            raise TypeError('Expected {}'.format(RequestBatch))

        return self._worker_pool.map(Requester.do, batch.requests)


class Requester(object):
    session = None

    @classmethod
    def do(cls, request):
        return request.do(cls.session)

    @classmethod
    def init_session(cls, session_args):
        if cls.session is not None:
            raise RequesterException('Requester session already initialized!')

        cls.session = requests.Session()
        cls.session.auth = session_args.get('auth')
        cls.session.verify = session_args.get('verify')
