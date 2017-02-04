from .serial_listener import SerialListener
from tornado.gen import coroutine
import re


class SonersServer(SerialListener):

    def __init__(self, handlers, *args, **kwargs):
        self.handlers = list(handlers or [])
        for spec in self.handlers:
            if not isinstance(spec, (tuple, list)):
                raise TypeError("Handler specs must be list or tuple")
            assert len(spec) in (2, 3, 4)

        super(SonersServer, self).__init__(*args, **kwargs)

    @coroutine
    def handle_stream(self, stream, device):
        future = stream.read_until(b'\n')
        if future is not None:
            result = yield future
            for spec in self.handlers:
                regular_expression, callback = spec
                match = re.match(regular_expression, result.decode("utf-8").rstrip())
                if match:
                    yield callback(device, **match.groupdict())
            # self.io_loop.add_future(future, lambda f: callback(f.result(), device))
