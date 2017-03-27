# coding:utf8

"""网络层模块"""

import json
import types
import shlex
import traceback
import subprocess

from fastweb.accesspoint import (web, coroutine, Task, Return, HTTPClient,
                                 AsyncHTTPClient, HTTPError, Subprocess, httpserver, ioloop)

from fastweb.loader import app
from fastweb.util.thread import FThread
from fastweb.util.python import to_plain
from fastweb.util.tool import timing, uniqueid
from fastweb.util.log import record, getLogger, recorder
from fastweb.exception import ComponentError, HttpError, SubProcessError


class Components(object):
    """组件基类
    基础组件功能
    """

    _blacklist = ['requestid', '_new_cookie', 'include_host',
                  '_active_modules', '_current_user', '_locale']

    def __init__(self):
        self.loader = app
        self.errcode = app.errcode
        self.configs = app.configs

        # 组件缓冲池,确保同一请求对同一组件只获取一次
        self._components = {}

    def __getattr__(self, name):
        """获取组件

        :parameter:
          - `name`:组件名称
        """

        if name in self._blacklist:
            raise AttributeError

        # 缓冲池中存在则使用缓冲池中的组件
        component = self._components.get(name)

        if not component:
            component = app.manager.get_component(name, self)

            if not component:
                self.recorder('ERROR', "can't acquire idle component <{name}>".format(name=name))
                raise ComponentError

            self._components[name] = component
            self.recorder('DEBUG', '{obj} get component from manager {name} {com}'.format(obj=self, name=name, com=component))
            return component
        else:
            self.recorder('DEBUG', '{obj} get component from components cache {name} {com}'.format(obj=self, name=name, com=component))
            return component

    @staticmethod
    def gen_requestid():
        """生成requestid"""

        return uniqueid()

    def add_blacklist(self, attr):
        """增加类属性黑名单

        :parameter:
          - `attr`:属性名称
        """

        self._blacklist.append(attr)

    def add_function(self, **kwargs):
        """增加方法到对象中"""

        # TODO:有没有更好的加载方式
        for callname, func in kwargs.items():
            setattr(self, '{callname}'.format(callname=callname), types.MethodType(func, self))

    def recorder(self, level, msg):
        """日志记录

        :parameter:
          - `level`:日志登记
          - `msg`:记录信息
        """

        record(level, msg, getLogger('application_recorder'), extra={'requestid': self.requestid})

    def release(self):
        """释放组件"""

        for name, component in self._components.items():
            app.manager.return_component(name, component)
            self.recorder('DEBUG', '{com} return manager'.format(com=component))

        self._components.clear()
        self.recorder('INFO', 'release all used components')


class SyncComponents(Components):
    """同步组件类"""

    def http_request(self, request):
        """http请求

        :parameter:
          - `request`:http请求
        """

        self.recorder('INFO', 'http request start {request}'.format(request=request))

        with timing('ms', 10) as t:
            try:
                response = HTTPClient(request)
            except HTTPError as ex:
                self.recorder('ERROR', 'http request error {request} {e}'.format(request=request, e=ex))
                raise HttpError

        self.recorder('INFO', 'http request successful\n{response} -- {time}'.format(response=response, time=t))
        return response

    def call_subprocess(self, command, stdin_data=None):
        """命令行调用

        :parameter:
          - `command`:命令行
          - `stdin_data`:传入数据
        """

        self.recorder('INFO', 'call subprocess start\n<{cmd}>'.format(cmd=command))

        with timing('ms', 10) as t:
            sub_process = subprocess.Popen(shlex.split(command),
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
            try:
                result, error = sub_process.communicate(stdin_data)
            except (OSError, ValueError) as ex:
                self.recorder('ERROR', 'call subprocess\n<{cmd}> ({e}) '.format(
                    cmd=command, e=ex, msg=result.strip() if result else error.strip()))
                raise SubProcessError

        if sub_process.returncode != 0:
            self.recorder('ERROR', 'call subprocess <{cmd}> <{time}> {msg}'.format(
                cmd=command, time=t, msg=result.strip() if result else error.strip()))
            raise SubProcessError

        self.recorder('INFO', 'call subprocess successful\n<{cmd}> <{time} {msg}>'.format(
            cmd=command, time=t, msg=result.strip() if result else error.strip()))
        return result, error


class AsynComponents(Components):
    """异步组件类"""

    @coroutine
    def http_request(self, request):
        """http请求

        :parameter:
          - `request`:http请求
        """

        self.recorder(
            'INFO', 'http request start\n{request}'.format(request=request))

        with timing('ms', 10) as t:
            try:
                response = yield AsyncHTTPClient().fetch(request)
            except HTTPError as ex:
                self.recorder('ERROR', 'http request error {request} ({e})'.format(
                    request=request, e=ex))
                raise HttpError

        self.recorder('INFO', 'http request successful\n{response} <{time}>'.format(
            response=response, time=t))
        raise Return(response)

    @coroutine
    def call_subprocess(self, command, stdin_data=None, stdin_async=True):
        """命令行调用

        :parameter:
          - `command`:命令行
          - `stdin_data`:传入数据
        """

        # TODO:待优化
        self.recorder(
            'INFO', 'call subprocess start <{cmd}>'.format(cmd=command))

        with timing('ms', 10) as t:
            stdin = Subprocess.STREAM if stdin_async else subprocess.PIPE
            sub_process = Subprocess(shlex.split(command),
                                     stdin=stdin,
                                     stdout=Subprocess.STREAM,
                                     stderr=Subprocess.STREAM)
            try:
                if stdin_data:
                    if stdin_async:
                        yield Task(sub_process.stdin.write, stdin_data)
                    else:
                        sub_process.stdin.write(stdin_data)

                if stdin_async or stdin_data:
                    sub_process.stdin.close()

                result, error = yield [Task(sub_process.stdout.read_until_close),
                                       Task(sub_process.stderr.read_until_close)]
            except (OSError, ValueError) as ex:
                self.recorder('ERROR', 'call subprocess <{cmd} <{time}> {e} {msg}'.format(
                    cmd=command, time=t, e=ex, msg=result.strip() if result else error.strip()))
                raise SubProcessError

        if sub_process.returncode != 0:
            self.recorder('ERROR', 'call subprocess <{cmd}> <{time}> {msg}'.format(
                cmd=command, time=t, msg=result.strip() if result else error.strip()))
            raise SubProcessError

        self.recorder('INFO', 'call subprocess <{cmd}> <{time} {msg}>'.format(
            cmd=command, time=t, msg=result.strip() if result else error.strip()))
        raise Return((result, error))

    def call_celery(self, *args, **kwargs):
        pass


class Api(web.RequestHandler, AsynComponents):
    """Api操作基类"""

    def __init__(self, application, request, **kwargs):
        super(Api, self).__init__(application, request, **kwargs)

        self.uri = request.uri
        self.host = request.host
        self.remoteip = request.remote_ip
        self.arguments = self.request.arguments
        self.requestid = self.get_argument('requestid') if self.get_argument('requestid', None) else self.gen_requestid()

        # TODO: 远程ip获取不准确
        self.recorder(
            'IMPORTANT',
            'Api request\nIp:<{ip}>\nHost:<{host}{uri}\nArguments:<{arguments}>\nUserAgent:<{ua}>'.format(
                ip=self.remoteip,
                host=self.host,
                uri=self.uri,
                arguments=self.request.body,
                ua=self.request.headers['User-Agent']))
        self.set_header_json()

    def data_received(self, chunk):
        pass

    def log_exception(self, typ, value, tb):
        """日志记录异常,并自动返回系统错误"""

        self.recorder('ERROR', '{message}'.format(
            message=traceback.format_exc()))
        self.end('SVR')

    def set_ajax_cors(self, allow_ip):
        """设置CORS"""

        header = 'Access-Control-Allow-Origin'
        self.set_header(header, allow_ip)
        self.recorder('INFO', 'set header <{key}:{ip}>'.format(
            key=header, ip=allow_ip))

    def set_header_json(self):
        """设置返回格式为json"""

        header = 'Content-type'
        self.add_header(header, 'text/json')
        self.recorder('INFO', 'set header <{key}:{type}>'.format(
            key=header, type='text/json'))

    def end(self, code='SUC', log=True, **kwargs):
        """请求结束"""

        ret = app.errcode[code]
        ret = dict(ret, **kwargs)
        self.write(json.dumps(ret))
        self.finish()
        self.release()
        t = (self.request._finish_time - self.request._start_time) * 1000

        if log:
            self.recorder(
                'IMPORTANT',
                'Api response\nResponse:<{ret}>\nTime:<{time}ms>'.format(
                    ret=ret, time=t))
        else:
            self.recorder(
                'IMPORTANT',
                'Api response\nTime:<{time}ms>'.format(time=t))


class Page(web.RequestHandler, AsynComponents):
    """Page操作基类"""

    def __init__(self, application, request, **kwargs):
        super(Page, self).__init__(application, request, **kwargs)

        self.uri = request.uri
        self.host = request.host
        self.remoteip = request.remote_ip
        self.arguments = self.request.arguments
        self.requestid = self.get_argument('requestid') if self.get_argument('requestid', None) else self.gen_requestid()

        self.recorder(
            'IMPORTANT',
            'Page request\nIp:<{ip}>\nHost:<{host}{uri}\nArguments:<{arguments}>\nUserAgent:<{ua}>'.format(
                ip=self.remoteip,
                host=self.host,
                uri=self.uri,
                arguments=self.request.body,
                ua=self.request.headers['User-Agent']))

    def data_received(self, chunk):
        pass

    def log_exception(self, typ, value, tb):
        """日志记录异常"""

        self.recorder('error', '{message}'.format(
            message=traceback.format_exc()))

    def end(self, template=None, log=True, **kwargs):
        """ 请求结束"""

        if template:
            # TODO:模版位置的正确性
            self.render(template, **kwargs)

        self.release()
        t = (self.request._finish_time - self.request._start_time) * 1000

        if log:
            self.recorder(
                'IMPORTANT',
                'Page response\nTemplate:{tem}\nTemArgs:{args}\nTime:<{time}ms>'.format(
                    tem=template, args=kwargs, time=t))
        else:
            self.recorder(
                'IMPORTANT',
                'Page response\nTemplate:{tem}\nTime:<{time}ms>'.format(
                    tem=template, time=t))


def arguments(convert=None, **ckargs):
    """检查并转换请求参数是否合法并转换参数类型

    :parameter:
      - `convert`:待转换的key,但非必要参数
      - `**ckargs`:必要参数
    """

    def _deco(fn):
        def _wrap(cls, *args, **kwargs):
            if convert:
                for cname, ctype in convert.items():
                    cvalue = cls.request.arguments.get(cname)
                    cvalue = to_plain(cvalue)
                    if cvalue:
                        cls.request.arguments[cname] = ctype(cvalue)

            for cname, ctype in ckargs.items():
                cvalue = cls.request.arguments.get(cname)
                cvalue = to_plain(cvalue)

                def invalid_recorder(msg):
                    diff = set(cls.request.arguments.keys()).symmetric_difference(set(ckargs.keys()))
                    cls.recorder('error', 'check arguments invalid <{diff}> {msg}'.format(
                        msg=msg, diff=to_plain(diff)))
                    cls.end('SVR')

                if cvalue:
                    if ctype is int:
                        if not cvalue.isdigit():
                            invalid_recorder('argument type error')
                            return
                    elif not isinstance(cvalue, ctype):
                        invalid_recorder('argument type error')
                        return
                else:
                    if isinstance(cls, Api):
                        invalid_recorder('argument empty')
                        return
                    elif isinstance(cls, Page):
                        invalid_recorder('argument empty')
                        return
                cls.request.arguments[cname] = ctype(cvalue)
            return fn(cls, *args, **kwargs)
        return _wrap
    return _deco


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
    try:
        ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        ioloop.IOLoop.current().stop()
        FThread.stop(0)
        recorder('INFO', 'server stop on {port}'.format(port=port))


def set_error_handler():
    # TODO:设置错误的句柄
    pass
