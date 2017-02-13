import falcon
import json
import cgi


class Head(object):
    def process_request(self, req, resp):
        if not req.content_type:
            return

        if 'application/json' not in req.content_type:
            raise falcon.HTTPUnsupportedMediaType('111', href='')
            if not req.client_accepts_json:
                raise falcon.HTTPNotAcceptable('222', href='')
        return


class Wrap(object):
    def process_request(self, req, resp):
        if req.content_length in (None, 0):
            req.context['doc'] = None
            return
        try:
            body = req.stream.read()
            req.context['doc'] = json.loads(body.decode('utf-8'))
        except:
            raise falcon.HTTPBadRequest('can not decode body', 'bbb')

    def process_response(self, req, resp, resource):
        if 'ret' not in req.context:
            return
        resp.body = json.dumps(req.context['ret'])


class Cors(object):
    def process_request(self, req, resp):
        resp.set_header('access-control-allow-origin', '*')
        resp.set_header('access-control-allow-methods', '*')
        resp.set_header('access-control-allow-headers', 'content-type')
        resp.set_header('access-control-allow-credentials', 'true')
        return


class Mult(object):
    class Parser(cgi.FieldStorage):
        pass

    def process_request(self, req, resp):
        if not req.content_type:
            return
        if 'multipart/form-data' not in req.content_type:
            return
        req.env.setdefault('QUERY_STRING', '')
        form = self.Parser(fp=req.stream, environ=req.env)
        for key in form:
            field = form[key]
            if not getattr(field, 'filename', False):
                field = form.getlist(key)
            req._params[key] = field
        return
