import functools
from . import HTTPConnectionInterceptor
from appdynamics.lang import urlparse


def intercept_tornado_httpclient(agent, mod):
    import tornado

    if getattr(tornado, 'version_info', (0, 0, 0, 0)) < (4, 1, 0, 0):
        agent.logger.warning("Older versions of tornado < 4.1.0.0 not are not supported. Skipping instrumentation")
    else:
        import tornado.httputil
        import tornado.stack_context

        class AsyncHTTPClientInterceptor(HTTPConnectionInterceptor):
            def end_exit_call(self, exit_call, future):
                super(AsyncHTTPClientInterceptor, self).end_exit_call(exit_call, exc_info=future.exc_info())

            def _fetch(self, fetch, client, request, callback=None, raise_error=True, **kwargs):
                exit_call = None
                with self.log_exceptions():
                    bt = self.bt
                    if bt:
                        if not isinstance(request, mod.HTTPRequest):
                            request = mod.HTTPRequest(url=request, **kwargs)

                        url = urlparse(request.url)
                        port = url.port or ('443' if url.scheme == 'https' else '80')
                        backend = self.get_backend(url.hostname, port, url.scheme, request.url)
                        if backend:
                            exit_call = self.start_exit_call(bt, backend, operation=url.path)
                            request.headers = tornado.httputil.HTTPHeaders(request.headers)
                            request.headers.add(*self.make_correlation_header(exit_call))

                future = fetch(client, request, callback=callback, raise_error=raise_error, **kwargs)
                future._callbacks.insert(0, functools.partial(tornado.stack_context.wrap(self.end_exit_call),
                                                              exit_call))
                return future

        AsyncHTTPClientInterceptor(agent, mod.AsyncHTTPClient).attach('fetch', wrapper_func=None)
