"""awh top namespace"""


import os
import functools
import collections
import contextlib

from werkzeug.wrappers import Request, Response


@contextlib.contextmanager
def _change_cwd(cwd):
    """A simple context manager which changes the CWD to the specified one and
    when it ends, changes it back to the current one."""
    current = os.getcwd()
    os.chdir(cwd)
    yield
    os.chdir(current)


class _Func:
    """Function wrapper which also supports some additional properties."""
    def __init__(self, func, *, cwd=os.getcwd()):
        self._func = func
        self._cwd = cwd

    def __call__(self, *args, **kwargs):
        with _change_cwd(self._cwd):
            return self._func(*args, **kwargs)


class Awh:
    """WSGI application class.

    In your application instantiate this class and when deploying point it as an
    application. It's similar to what Flask does.

        from awh import Awh
        app = Awh()
    """

    class _Reg:
        validator = None
        executor = None

    def __init__(self):
        self._registry = collections.OrderedDict()
        self._resp_manipulator = None

    def register_validator(self, name, func, **props):
        """Same as decorator @validator, but as a function call."""
        return self._register_func(name, func, 'validator', **props)

    def validator(self, name, **props):
        """Decorator which registers a function as a validator for a given
        webhook's name. When called, validators receive Request object.

        Example:
            @app.validator('foo')
            def my_validator(request):
                return request.form['bar'] != 'blah'
        """

        def _decorator(func):
            func_wrapper = self.register_validator(name, func, **props)

            @functools.wraps(func)
            def _wrapper(*args, **kwargs):
                return func_wrapper(*args, **kwargs)
            return _wrapper
        return _decorator

    def register_executor(self, name, func, **props):
        """Same as decorator @executor, but as a function call."""
        return self._register_func(name, func, 'executor', **props)

    def executor(self, name, **props):
        """Decorator which registers a function as a executor for a given
        webhook's name. Executors are called when a corresponding validator
        returns True. When called, executors receive Request object.

        Example:
            @app.executor('foo')
            def my_executor(request):
                subprocess.call(['command'])
        """
        def _decorator(func):
            func_wrapper = self.register_executor(name, func, **props)

            @functools.wraps(func)
            def _wrapper(*args, **kwargs):
                return func_wrapper(*args, **kwargs)
            return _wrapper
        return _decorator

    def clear(self):
        """Removes all registered executors and validators"""
        self._registry.clear()

    def app(self, func):
        """Decorator which registers a function as a response handler.

        Response handler is basically a wrapped WSGI application which accepts
        incoming request and returns a result. It can throw any exception in
        which case no registered validators and executors will be processed (but
        modified response will still be sent back).

        Request and Response passed to registered function are werkzeug's
        objects. Refer to its documentation for further informations on how they
        work:
            http://werkzeug.pocoo.org/docs/0.11/wrappers/

        Example:
            from awh import Awh
            app = Awh()

            @app.app
            def main(request, response, data):
                response.status_code = 404
                data['foo'] = 'bar'
        """

        if self._resp_manipulator is not None:
            raise ValueError('multiple applications registered')
        self._resp_manipulator = func

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return _wrapper

    def wsgi_app(self, environ, start_response):
        """Actual WSGI application."""
        request = Request(environ)
        response = Response()

        try:
            data_dict = {}
            if self._resp_manipulator is not None:
                self._resp_manipulator(request, response, data_dict)
        except Exception:
            return response(environ, start_response)

        self._call_executors(request, data_dict)
        return response(environ, start_response)

    def _call_executors(self, request, data_dict):
        for _, reg in self._registry.items():
            if reg.validator and reg.executor:
                try:
                    if reg.validator(request, data_dict):
                        reg.executor(request, data_dict)
                except Exception:
                    pass

    def _register_func(self, name, func, t, **props):
        reg = self._registry.setdefault(name, Awh._Reg())
        if getattr(reg, t, None) is not None:
            raise ValueError('multiple %ss for %s' % (t, name))
        setattr(reg, t, _Func(func, **props))
        return getattr(reg, t)

    def __call__(self, environ, start_response):
        """Makes Awh callable, so it can be registered as a valid WSGI
        application."""
        return self.wsgi_app(environ, start_response)
