from flask import Response, jsonify


class ServiceResponse(Response):

    def __init__(self, *args, **kwargs):
        if 'direct_passthrough' not in kwargs:
            kwargs['direct_passthrough'] = True
        kwargs["content_type"] = "application/json"
        data = kwargs["response"]
        kwargs["response"] = {"data": data, "len": len(data), "error": False}
        super(ServiceResponse, self).__init__(*args, **kwargs)

    @classmethod
    def force_type(cls, rv, environ=None):
        if isinstance(rv, dict):
            rv = jsonify(rv)
        return super(ServiceResponse, cls).force_type(rv, environ)
