# -*- coding: utf-8 -*-


import hashlib
import requests

from datetime import datetime
from .base import BackendError, Map


class Unidata(object):

    def __init__(self, host, key=None, timeout=20):
        self.host = host
        self.key = key
        self.timeout = timeout
        self._sess = requests.Session()

    def _sign(self, data):
        if not self.key:
            return
        data = data or dict()
        s = ''
        for key, value in sorted(data.items()):
            s += '&{}={}'.format(key, value)
        s += '&key={}'.format(self.key)
        sign = hashlib.sha1(s[1:]).hexdigest()
        data['sign'] = sign

    def usage(self, msisdn):
        usage = self.do("GET", "/cards/show", dict(msisdn=msisdn))
        return self._make_usage(usage)

    def status(self, msisdn):
        data = self.do("GET", "/cards/status", dict(msisdn=msisdn))
        return data

    def _make_usage(self, usage):
        if usage.expired_at:
            usage.expired_at = datetime.strptime(usage.expired_at, "%Y-%m-%d %H:%M:%S")
        if usage.activated_at:
            usage.activated_at = datetime.strptime(usage.activated_at, "%Y-%m-%d %H:%M:%S")
        return usage

    def daily(self, type=0, limit=12):
        data = self.do("GET", "/cards/daily", dict(type=type, limit=limit))
        data = [(k, v) for k, v in data]
        data.sort(key=lambda x: int(x[0].replace('-', '')))
        return data

    def batch_usage(self, *msisdns):
        if not msisdns:
            return []
        usages = self.do("GET", "/cards/lookup", dict(msisdn=",".join(msisdns)))
        return filter(self._make_usage, usages)

    def charge(self, msisdn, data, day, cause='', user_ip=''):
        data = dict(msisdn=msisdn, data=data, day=day, cause=cause)
        if user_ip:
            data.update(dict(user_ip=user_ip))
        return self.do("POST", "/cards/charge", data)

    def detail(self, msisdn):
        data = dict(msisdn=msisdn)
        return self.do("GET", "/cards/detail", data)

    def activated(self, msisdn):
        data = dict(msisdn=msisdn)
        return self.do("POST", "/cards/activated", data)

    def deactivated(self, msisdn):
        data = dict(msisdn=msisdn)
        return self.do("POST", "/cards/deactivated", data)

    def ready(self, msisdn):
        data = dict(msisdn=msisdn)
        return self.do("POST", "/cards/ready", data)

    def do(self, method, path, data):
        data and self._sign(data)
        params = None
        if method == "GET":
            params, data = data, None
        url = "{}{}".format(self.host, path)
        req = requests.Request(method, url, params=params, data=data)
        prepared = req.prepare()
        prepared.headers["User-Agent"] = "yilian/v0.1"
        if method == "POST":
            prepared.headers["Content-Type"] = "application/x-www-form-urlencoded"
        resp = self._sess.send(prepared, timeout=self.timeout)
        status_code = resp.status_code
        body = resp.json()
        if isinstance(body, dict):
            body = Map(body)
        elif isinstance(body, list):
            for idx, one in enumerate(body):
                if isinstance(one, dict):
                    one = Map(one)
                body[idx] = one
        if 500 <= status_code < 600:
            raise BackendError("Status Code: {0}".format(status_code))
        if 400 <= status_code < 500:
            raise BackendError(body.message)
        return body
