# coding: utf-8
import logging
import signal
import time
from abc import ABCMeta
from abc import abstractmethod

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.web import RequestHandler

from dsn_tornado.session import Session
from dsn_tornado.session import SessionManager

_DSN_COOKIE_NAME_SESSION_ID = '_dsn_session_id'
_DSN_GLOBAL_RESOURCES = '_dsn_global_resources'
_DSN_SESSION_MANAGER = 'session_manager'

_READ_ONLY_RESOURCES = {_DSN_SESSION_MANAGER: True}

_DEFAULT_TORNADO_SETTINGS = {
    # support for nginx
    'xheaders': True,
}


def _get_logger():
    return logging.getLogger('dsn.tornado.server')


class RequestHandlerWrapper(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super(RequestHandlerWrapper, self).__init__(
            application=application, request=request, **kwargs)
        self.__logger = _get_logger()

    def initialize(self):
        pass

    def prepare(self):
        pass

    def set_default_headers(self):
        pass

    def get_resource(self, name: str):
        assert name, '[name] is None'
        return self.settings[_DSN_GLOBAL_RESOURCES].get(name)

    @property
    def is_debug(self) -> bool:
        return self.settings.get('debug', False)

    @property
    def session_manager(self) -> SessionManager:
        return self.get_resource(name=_DSN_SESSION_MANAGER)

    def get_current_session(self) -> Session:
        # self.__logger.debug('call get_current_session')
        session: Session = None
        if self.session_manager is None:
            self.__logger.warning('SessionManager is not available')
            return session
        value = self.get_secure_cookie(name=_DSN_COOKIE_NAME_SESSION_ID)
        sid = None
        if type(value) is bytes:
            sid = value.decode('ASCII')
        if sid is None:
            return session
        if self.session_manager.exists(session_id=sid):
            # load session
            session = self.session_manager.get(session_id=sid)
        return session

    def set_current_session(self, session: Session, domain=None, path='/'):
        # self.__logger.debug('call set_current_session')
        if self.session_manager is None:
            self.__logger.warning('SessionManager is not available')
            return
        sid = session.id
        protocol = self.request.protocol.lower()
        # print('request.protocol=' + protocol)
        secure = protocol == 'https'
        self.set_secure_cookie(name=_DSN_COOKIE_NAME_SESSION_ID, value=sid,
                               domain=domain, path=path, secure=secure, httponly=True)

    def get_current_user(self) -> Session:
        # self.__logger.debug('call get_current_user')
        session = None
        if self.session_manager is not None:
            session = self.get_current_session()
        return session


class ApplicationFactory(metaclass=ABCMeta):
    @abstractmethod
    def create(self) -> Application:
        pass


class HttpServerWrapper:
    def __init__(self, app: Application,
                 address: str = '127.0.0.1',
                 port: int = 8080,
                 tornado_settings: dict = _DEFAULT_TORNADO_SETTINGS,
                 shutdown_timeout: int = 5,
                 session_manager: SessionManager = None):
        assert app, 'Application is None'
        assert shutdown_timeout >= 0, 'shutdown_timeout must greater or equal to 0'
        self.__logger = _get_logger()
        self.__app = app
        self.__address = address
        self.__port = port
        self.__http_server = None
        self.__resources = dict()
        self.__tornado_settings = tornado_settings
        self.__shutdown_timeout = shutdown_timeout
        self.__running = False
        self.__resources[_DSN_SESSION_MANAGER] = session_manager
        # set shutdown timeout
        self.__shutdown_timeout = shutdown_timeout
        self.__logger.info('set [shutdown_timeout]=[%s]seconds', self.__shutdown_timeout)

    @property
    def address(self) -> str:
        return self.__address

    @property
    def port(self) -> int:
        return self.__port

    @property
    def session_manager(self):
        return self.__resources.get(_DSN_SESSION_MANAGER)

    def set_resource(self, name, value):
        assert not self.__running, 'server already running'
        assert name, 'resource name is None'
        if _READ_ONLY_RESOURCES.get(name, False):
            self.__logger.warning('[%s] is read-only resource' % name)
        else:
            self.__resources[name] = value

    def run(self):
        assert not self.__running, 'server already running'
        self.__running = True
        self.__app.settings[_DSN_GLOBAL_RESOURCES] = self.__resources
        # build http server
        self.__http_server = HTTPServer(self.__app, **self.__tornado_settings)
        self.__http_server.listen(address=self.address, port=self.port)
        self.__logger.info('listen on [%s:%d]' % (self.address, self.port))

        signal.signal(signal.SIGTERM, self.__shutdown_handler)
        signal.signal(signal.SIGINT, self.__shutdown_handler)
        self.__logger.info('start server process')
        IOLoop.current().start()
        self.__logger.info('server process stopped')

    def __shutdown(self):
        self.__logger.info('try to shutdown server')
        self.__running = False
        self.__http_server.stop()
        self.__http_server.close_all_connections()
        self.__http_server = None

    def __stop_io_loop(self):
        self.__logger.debug('timeout : [%i] seconds', self.__shutdown_timeout)
        IOLoop.current().stop()

    def __shutdown_handler(self, sig, frame):
        self.__logger.debug('caught signal: %s frame: %s', sig, frame.f_code.co_name)

        deadline = time.time() + self.__shutdown_timeout
        io_loop = IOLoop.current()
        io_loop.add_callback_from_signal(callback=self.__shutdown)
        io_loop.add_timeout(deadline=deadline, callback=self.__stop_io_loop)
