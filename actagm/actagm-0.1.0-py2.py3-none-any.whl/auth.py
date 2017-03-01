from requests.auth import AuthBase


class AgmAuth(AuthBase):
    """Attaches Actifio Authentication to the given Request object."""

    def __init__(self, sessionid):
        self.sid = sessionid

    def __eq__(self, other):
        return self.sid == other.sid

    def __ne__(self, other):
        return not self == other

    def __call__(self, r):
        r.headers['Authorization'] = "Actifio " + self.sid
        return r
