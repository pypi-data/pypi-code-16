from tornado.ioloop import IOLoop
from functools import partial


def create_url(base_url, *, tld, path):
    return base_url + tld + path


def wait(f, *args, **kwargs):
    loaded_f = partial(f, *args, **kwargs)
    return IOLoop.current().run_sync(loaded_f)
