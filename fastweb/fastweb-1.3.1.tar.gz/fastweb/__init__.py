# coding:utf8


from tornado.locks import Condition
from tornado.options import options
from tornado.gen import coroutine, Return, Task, sleep
from tornado import gen, web, httpserver, ioloop
from tornado.web import UIModule as UI, asynchronous
from tornado.httpclient import HTTPRequest as Request

from fastweb.loader import app
from fastweb.util.log import recorder
from fastweb.pattern import SyncPattern, AsynPattern
from fastweb.core import Api, Page, SyncComponents, AsynComponents, checkArgument


def start_server(port, handlers, **settings):
    """启动服务器"""

    application = web.Application(
        handlers,
        **settings
    )

    http_server = httpserver.HTTPServer(
        application, xheaders=settings.get('xheaders'))
    http_server.listen(port)
    recorder('INFO', 'server start on {port}'.format(port=port))
    ioloop.IOLoop.instance().set_blocking_log_threshold(5)
    ioloop.IOLoop.instance().start()
    recorder('INFO', 'server stop on {port}'.format(port=port))
    # ioloop.IOLoop.instance().close()


def set_errcode_handler(**kwargs):
    pass
