from .funcs import chain, stop
from .funcs.errors import setStatus, defaultErrors

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re

class Router:
    """ Provides Routing for application logic. """
    def __init__(self, name=None):
        self.name, self.handlers = name, []
    # Methods to add handlers for every http request method
    def options(self, path, handler=None, name=None):
        return self.method('OPTIONS', path, handler, name)
    def get(self, path, handler=None, name=None):
        return self.method('GET', path, handler, name)
    def head(self, path, handler=None, name=None):
        return self.method('HEAD', path, handler, name)
    def post(self, path, handler=None, name=None):
        return self.method('POST', path, handler, name)
    def put(self, path, handler=None, name=None):
        return self.method('PUT', path, handler, name)
    def patch(self, path, handler=None, name=None):
        return self.method('PATCH', path, handler, name)
    def delete(self, path, handler=None, name=None):
        return self.method('DELETE', path, handler, name)
    def trace(self, path, handler=None, name=None):
        return self.method('TRACE', path, handler, name)
    def connect(self, path, handler=None, name=None):
        return self.method('CONNECT', path, handler, name)
    # Methods to add handlers for errors
    def error(self, code, path, handler):
        return self.method(code, path, chain(setStatus(code), handler), name)
    # Method to add handlers that will be used for every method
    def use(self, path, handler=None, name=None):
        return self.method('USE', path, handler, name)
    # Shortcut for creating a subrouter
    def route(self, path, name=None):
        router = Router(name)
        self.method('USE', path, router)
        return router
    # General method for adding a method
    def method(self, method, path, handler=None, name=None):
        if isinstance(method, (list, tuple)):
            for m in method:
                self.method(m, path, handler)
            return self
        if handler is None:
            self.handlers.append((method, re.compile(r'^'), path))
            return self
        if method == 'USE' and isinstance(handler, Router):
            self.handlers.append((method, re.compile(path), handler))
            return self
        self.handlers.append(('USE', re.compile(path), Router(name).method(method, handler)))
        return self
    # Try to match a method and path to this router
    def match(self, method, path):
        handlers, args, kwargs = [], [], {}
        found, exists = False, False
        for method_, path_, handler in self.handlers:
            match = path_.search(path)
            if match and (method_ == method or method_ == 'USE'):
                if method_ != 'USE':
                    found, exists = True, True
                args += match.groups()
                kwargs = {**kwargs, **match.groupdict()}
                if isinstance(handler, Router):
                    handlers_, args_, kwargs_ = handler.match(method, path[:match.start()] + path[match.end():])
                    args += args_
                    kwargs = {**kwargs, **kwargs_}
                    if handlers_ is not None:
                        exists = True
                        if handlers_ != []:
                            found = True
                            handlers += handlers_
                else:
                    handlers.append(handler)
            elif not isinstance(method_, int):
                exists = True
        return ((handler if found else []) if exists else None), args, kwargs
    # Turns a Request object into a Response object according to how this app is defined
    def resolve(self, req):
        handler, args, kwargs = self.match(req.method, req.path)
        if handler is None:
            handler, args, kwargs = self.match(404, req.path)
        if handler is None:
            handler, args, kwargs = defaultErrors[404], [], {}
        if handler == []:
            handler, args, kwargs = self.match(405, req.path)
        if handler == []:
            handler, args, kwargs = defaultErrors[405], [], {}
        res = Response()
        chain(handler, stop)(req, res, None)
        return res
    # Start a server from this router
    def listen(app, host='127.0.0.1', port=8000):
        # Define handler
        class Handler(BaseHTTPRequestHandler):
            def __getattr__(self, key):
                if key.startswith('do_'):
                    return self.do
                raise AttributeError()
            def do(self):
                req = Request(self)
                res = app.resolve(req)
                res.respond(self)
        # Start server
        httpd = HTTPServer((host, port), Handler)
        print('Running app on ' + host + ':' + str(port))
        httpd.serve_forever()

class Request:
    """ Provides the data sent by a request. """
    def __init__(self, handler):
        self.method, self.path = handler.command, handler.path.rstrip('/')
        self.endpoint = None

class Response:
    """ Keeps track of the data we need to respond to a request. """
    def __init__(self, status=200, content_type=None, body=None):
        self.__status, self.__content_type, self.__body = status, content_type, body
    # Functions for managing status
    def status(self, status=None):
        self.__status = status
        return self
    def getStatus(self):
        return self.__status
    # Functions for managing content-type
    def contentType(self, content_type=None):
        self.__content_type = content_type
        return self
    def getContentType(self):
        return self.__content_type
    # Functions for managing body
    def body(self, body=None):
        self.__body = body
        return self
    def getBody(self):
        return self.__body
    # Shortcuts for inserting specific kinds of data
    def html(self, html):
        self.contentType('text/html').body(html)
    def json(self, obj):
        self.contentType('application/json').body(json.dumps(obj))
    def text(self, text):
        self.contentType('text/plain').body(text)
    # Respond to a request handler using this response
    def respond(self, handler):
        handler.send_response(self.__status)
        handler.send_header('Content-type', self.__content_type)
        handler.end_headers()
        handler.wfile.write(bytes(self.__body, "utf8"))
