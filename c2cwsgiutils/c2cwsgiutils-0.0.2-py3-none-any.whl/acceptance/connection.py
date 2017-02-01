import re
import requests

COLON_SPLIT_RE = re.compile(r'\s*,\s*')


class Connection:
    def __init__(self, base_url, origin):
        self.base_url = base_url
        self.session = requests.session()
        self.origin = origin

    def get(self, url, expected_status=200, params=None, headers={}, cors=True):
        """
        get the given URL (relative to the root of API).
        """
        r = self.session.get(self.base_url + url, params=params, headers=self._merge_headers(headers, cors))
        try:
            check_response(r, expected_status, cache_allowed=False)
            self._check_cors(cors, r)
            return r.text
        finally:
            r.close()

    def get_json(self, url, expected_status=200, params=None, headers={}, cors=True):
        """
        get the given URL (relative to the root of API).
        """
        r = self.session.get(self.base_url + url, params=params, headers=self._merge_headers(headers, cors))
        try:
            check_response(r, expected_status, cache_allowed=False)
            self._check_cors(cors, r)
            return r.json()
        finally:
            r.close()

    def post_json(self, url, json=None, expected_status=200, headers={}, cors=True):
        """
        POST the given URL (relative to the root of API).
        """
        r = self.session.post(self.base_url + url, json=json, headers=self._merge_headers(headers, cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.json()
        finally:
            r.close()

    def put_json(self, url, json=None, expected_status=200, headers={}, cors=True):
        """
        POST the given URL (relative to the root of API).
        """
        r = self.session.put(self.base_url + url, json=json, headers=self._merge_headers(headers, cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r.json()
        finally:
            r.close()

    def delete(self, url, expected_status=204, headers={}, cors=True):
        """
        DELETE the given URL (relative to the root of API).
        """
        r = self.session.delete(self.base_url + url, headers=self._merge_headers(headers, cors))
        try:
            check_response(r, expected_status)
            self._check_cors(cors, r)
            return r
        finally:
            r.close()

    def _cors_headers(self, cors):
        if cors:
            return {
                "Origin": self.origin
            }
        else:
            return {}

    def _check_cors(self, cors, r):
        if cors:
            assert r.headers["Access-Control-Allow-Origin"] == "*"

    def _merge_headers(self, headers, cors):
        merged = dict(headers)
        merged.update(self.session.headers)
        merged.update(self._cors_headers(cors))
        return merged


def check_response(r, expected_status=200, cache_allowed=True):
    if isinstance(expected_status, tuple):
        assert r.status_code in expected_status, "status=%d\n%s" % (r.status_code, r.text)
    else:
        assert r.status_code == expected_status, "status=%d\n%s" % (r.status_code, r.text)

    if not cache_allowed:
        # Cache is the root of all evil. Must never be enabled
        assert 'Cache-Control' in r.headers
        cache_control = COLON_SPLIT_RE.split(r.headers['Cache-Control'])
        assert 'no-cache' in cache_control
