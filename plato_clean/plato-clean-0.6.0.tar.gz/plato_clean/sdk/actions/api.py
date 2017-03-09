from .. import conn


class _API(object):
    """
    actions underlying api
    """
    def __init__(self):
        pass

    def configure(self, access_key, access_secret, endpoint, is_debug):
        """
        """
        if not endpoint.endswith('/'):
            endpoint += '/'

        self.conn = conn.Conn(access_key,
                              access_secret,
                              endpoint,
                              is_debug)

API = _API()


def setup(access_key, access_secret, endpoint, is_debug=False):
    # config this api.
    API.configure(access_key,
                  access_secret,
                  endpoint,
                  is_debug)
    return API
