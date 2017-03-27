# coding:utf8

"""第三方接入模块"""


import tornado
from tornado import web, iostream
from tornado.locks import Condition
from tornado.options import options
from tornado.process import Subprocess
from tornado.web import UIModule, asynchronous
from tornado import gen, web, httpserver, ioloop
from tornado.httpclient import HTTPRequest as Request
from tornado.gen import coroutine, Return, Task, sleep
from tornado.httpclient import HTTPClient, AsyncHTTPClient, HTTPError, HTTPRequest

from celery import Task as celeryTask

from thrift.server import TServer
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol