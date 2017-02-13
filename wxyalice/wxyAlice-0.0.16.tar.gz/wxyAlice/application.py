from gevent import pywsgi
import falcon


class Application(object):
    def __init__(self, me):
        self._me = (me['host'], me['port'])

    def Install(self, mid, res):
        self.app = falcon.API(middleware=mid)
        map(lambda x: self.app.add_route(x[0], x[1]),  res)

    def Forever(self):
        pywsgi.WSGIServer(self._me, self.app).serve_forever()
