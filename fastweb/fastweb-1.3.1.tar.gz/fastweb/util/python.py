# coding:utf8

"""python特性"""

import six
import json
from thrift.TTornado import TTransportException

import fastweb
from fastweb import coroutine, Return, sleep


head = lambda o, h: '{head}{ori}'.format(head=h, ori=o)


def format(st, whole=0):
    if whole:
        return '\n'.join([head(e, whole*' ') for e in st.split('\n')])
    else:
        return st


def dumps(obj, indent, whole=0):
    if whole:
        return '\n'.join([head(e, whole*' ') for e in json.dumps(obj, indent=indent).split('\n')])
    else:
        return json.dumps(obj, indent=indent)


def to_iter(e):
    """转换可迭代形式"""

    if isinstance(e, (six.string_types, six.string_types, six.class_types, six.text_type, six.binary_type)):
        return (e)
    elif isinstance(e, list):
        return (e)


def to_plain(i):
    """转换不可迭代形式"""

    if isinstance(i, dict):
        plain = ''
        for key, value in i:
            plain += "{key}:{value}".format(key=key, value=value)
        return plain
    elif isinstance(i, (list, set)):
        return ','.join(i)
    else:
        return i


def mixin(cls, mixcls, resume=False):
    """动态继承"""

    mixcls = to_iter(mixcls)

    if resume:
        cls.__bases__ = mixcls
    else:
        for mcls in mixcls:
            cls.__bases__ += (mcls,)


class ExceptionProcessor(object):
    """异常处理器"""

    def __init__(self, exception, processor):
        self.exception = exception
        self.processor = processor


class AsynProxyCall(object):
    """异步调用代理,用来解决__getattr__无法传递多个参数的问题"""

    def __init__(self, proxy, method, throw_exception=None, exception_processor=None):
        self.proxy = proxy
        self._method = method
        self._throw_exception = throw_exception
        self._exception_processor = exception_processor
        self._arg = None
        self._kwargs = None

    @coroutine
    def __call__(self, *arg, **kwargs):
        self._arg = arg
        self._kwargs = kwargs
        self.proxy.recorder('INFO', 'call {proxy} <{method}> start')
        try:
            with fastweb.util.tool.timing('ms', 8) as t:
                yield getattr(self.proxy._other, self._method)(*arg, **kwargs)
            self.proxy.recorder('INFO', 'call {proxy} <{method}> success <{time}>'.format(proxy=self.proxy,
                                                                                           method=self._method, time=t))
            raise Return()
        except TTransportException as e:
            self.proxy.recorder('ERROR',
                                 'call {proxy} <{method}> error {e} ({msg})\nreconnect'.format(proxy=self.proxy,
                                                                                               method=self._method,
                                                                                               e=type(e), msg=e))
            yield self._exception_processor.processor()
            self(*self._arg, **self._kwargs)
        else:
            raise self._throw_exception
