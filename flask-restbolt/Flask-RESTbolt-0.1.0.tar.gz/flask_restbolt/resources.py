#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Mapping

from flask import request
from flask.views import MethodView
from flask_restbolt import unpack
from ordereddict import OrderedDict
from werkzeug.wrappers import Response as ResponseBase

__author__ = 'costular'


# TODO use Mixins instead

class Resource(MethodView):
    """
    Represents an abstract RESTful resource. Concrete resources should
    extend from this class and expose methods for each supported HTTP
    method. If a resource is invoked with an unsupported HTTP method,
    the API will return a response with status 405 Method Not Allowed.
    Otherwise the appropriate method is called and passed all arguments
    from the url rule used when adding the resource to an Api instance. See
    :meth:`~flask_restbolt.Api.add_resource` for details.
    """
    representations = None
    pagination = None
    permissions = []
    method_decorators = []

    def get(self):
        raise NotImplementedError()

    def post(self):
        raise NotImplementedError()

    def put(self):
        raise NotImplementedError()

    def patch(self):
        raise NotImplementedError()

    def delete(self):
        raise NotImplementedError()

    def dispatch_request(self, *args, **kwargs):
        # Taken from flask
        #noinspection PyUnresolvedReferences
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        for decorator in decorators:
            meth = decorator(meth)

        resp = meth(*args, **kwargs)

        if isinstance(resp, ResponseBase):  # There may be a better way to test
            return resp

        representations = self.representations or OrderedDict()

        #noinspection PyUnresolvedReferences
        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
            return resp

        return resp


class ResourceModel(Resource):
    model = None
    serializer = None
    db = None

    def get(self, id=None):
        if not self.model:
            raise ValueError("Model must be provided.")
        if not self.serializer:
            raise ValueError("Serializer must be provided")

        if not id:
            objects = self.model.query.all()
            data = self.serializer(many=True).dump(objects).data
            return data

        object = self.model.query.find_by(id=id).first()
        data = self.serializer().dump(object).data
        return data

    def post(self):
        pass

    def put(self, id=None):
        pass

    def patch(self, id=None):
        pass

    def delete(self, id=None):
        pass