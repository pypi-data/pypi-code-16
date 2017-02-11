import requests.auth


class HTTPBearerAuth(requests.auth.AuthBase):

    def __init__(self, bearer_token):
        self.bearer_token = bearer_token

    def __eq__(self, other):
        return self.bearer_token == getattr(other, 'bearer_token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, req):
        req.headers['Authorization'] = 'Bearer ' + self.bearer_token
        return req


class HTTPTokenAuth(requests.auth.AuthBase):

    def __init__(self, auth_token):
        self.auth_token = auth_token

    def __eq__(self, other):
        return self.auth_token == getattr(other, 'auth_token', None)

    def __ne__(self, other):
        return not self == other

    def __call__(self, req):
        req.headers['Authorization'] = 'Token token={}'.format(self.auth_token)
        return req
