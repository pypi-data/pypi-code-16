from flask import request

from fake_ubersmith.api.base import Base


class UbersmithBase(Base):
    def __init__(self, data_store):
        super().__init__(data_store)

    def hook_to(self, server):
        self.app = server
        self.app.add_url_rule(
            '/api/2.0/', view_func=self._route_method,
            methods=["POST"]
        )

    def register_endpoints(self, ubersmith_method, function):
        self.methods[ubersmith_method] = function

    def _route_method(self):
        return self.methods[request.form['method']](request.form)


class FakeUbersmithError:
    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message
