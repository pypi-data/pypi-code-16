import os
import threading
from http import server


class TestServer:
    """
    Runner for http.server simple server.
    """

    @property
    def base_url(self):
        return 'http://localhost:%s/' % self.port

    @property
    def running(self):
        return self._target is not None

    def __init__(self, port=8000, path=None, poll_interval=0.5):
        path = path or os.getcwd()
        self.port = port
        self.path = path
        self._target = None
        self._server_obj = None
        self.poll_interval = poll_interval

    def _prepare_to_serve(self):
        class HTTPHandler(BaseHTTPHandler):
            cwd = self.path

        addr = ('', self.port)
        self._server_obj = server.HTTPServer(addr, HTTPHandler)

    def start(self):
        """
        Starts serving in the background.
        """

        self._prepare_to_serve()
        self._target = threading.Thread(target=self._server_obj.serve_forever,
                                        daemon=True,
                                        args=(self.poll_interval,))
        self._target.start()

    def serve_forever(self, poll_interval=None):
        """
        Starts serving blocking control flow.
        """

        if poll_interval is None:
            poll_interval = self.poll_interval
        self._prepare_to_serve()
        self._target = True  # Makes .stop() works from another thread
        self._server_obj.serve_forever(poll_interval)

    def stop(self):
        """
        Stops server.
        """

        if self._target is not None:
            self._server_obj.shutdown()
            self._target.join(timeout=self.poll_interval)
            self._server_obj.server_close()
        self._target = None


class BaseHTTPHandler(server.SimpleHTTPRequestHandler):
    local_cwd = os.getcwd()

    @property
    def cwd(self):
        raise NotImplementedError

    def translate_path(self, path):
        new_path = super().translate_path(path)

        if new_path.startswith(self.local_cwd):
            new_path = new_path[len(self.local_cwd) + 1:]
            new_path = os.path.join(self.cwd, new_path)
        return new_path


if __name__ == '__main__':
    import random
    mod_path = os.path.dirname(__file__)
    port = random.randint(8001, 65535)
    test_path = os.path.join(mod_path, 'tests', 'data')
    print('Starting server in port %s, at %r' % (port, test_path))
    server_instance = TestServer(port=port, path=test_path)
    server_instance.serve_forever()