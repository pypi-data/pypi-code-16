# coding:utf8

"""系统全局加载模块"""


import json

from fastweb import ioloop
from fastweb.manager import Manager
from fastweb.util.tool import timing
from fastweb.exception import FastwebException
from fastweb.setting.default_errcode import ERRCODE
from fastweb.pattern import SyncPattern, AsynPattern
from fastweb.util.configuration import Configuration
from fastweb.util.log import get_yaml_logging_setting, setup_logging, getLogger, recorder, check_logging_level


class Loader(object):
    """系统全局加载器

    TODO:关于导入机制的问题
    """

    def __init__(self):
        # 配置
        self.configs = None
        self.configer = None

        # 日志配置
        self.system_recorder = None
        self.application_recorder = None

        # 管理器
        self.manager = None
        self.pattern = None

        # 系统错误码
        self.errcode = None

    def load_recorder(self, application_log_path, system_log_path=None, logging_setting_path=None, logging_setting=None, application_level='DEBUG', system_level='DEBUG'):
        """加载日志对象

        需要最先加载,因为其他加载都需要使用recorder

        :parameter:
          - `app_log_path`:应用日志路径
          - `system_log_path`:系统日志路径,默认系统日志路径和应用日志路径相同
          - `logging_setting_path`:默认从fastweb.settting.default_logging.yaml获取配置,可以指定为自定义的日志配置
          - `logging_setting`:自定以logging配置
          - `application_level`:应用日志输出级别
          - `system_level`:系统日志输出级别
        """

        if not logging_setting:
            logging_setting = get_yaml_logging_setting(logging_setting_path) if logging_setting_path else get_yaml_logging_setting()
            logging_setting['handlers']['application_file_time_handler']['filename'] = application_log_path
            logging_setting['handlers']['system_file_size_handler']['filename'] = system_log_path if system_log_path else application_log_path

        if application_level:
            check_logging_level(application_level)
            logging_setting['loggers']['application_recorder']['level'] = application_level

        if system_level:
            check_logging_level(system_level)
            logging_setting['loggers']['system_recorder']['level'] = system_level

        setup_logging(logging_setting)

        self.system_recorder = getLogger('system_recorder')
        self.application_recorder = getLogger('application_recorder')

        recorder('INFO', 'load recorder configuration\n{conf}\n\napplication log: {app_path} [{app_level}]\nsystem log: {sys_path} [{sys_level}]'.format(conf=json.dumps(logging_setting, indent=4), app_path=application_log_path, app_level=application_level, sys_path=system_log_path, sys_level=system_level))

    def load_configuration(self, backend='ini', **setting):
        """加载配置文件,组件配置文件

        :parameter:
          - `path`:配置文件路径
        """

        if not self.system_recorder and not self.application_recorder:
            recorder('CRITICAL', 'please load recorder first!')
            raise FastwebException

        self.configer = Configuration(backend, **setting)
        self.configs = self.configer.configs

        recorder('INFO', 'load configuration\nbackend:\t{backend}\nsetting:\t{setting}'.format(backend=backend, setting=setting))

    def load_manager(self, pattern):
        """加载管理器

        需要在load_configuration后进行

        :parameter:
          - `pattern`:同步或异步模式,SyncPattern或者AsynPattern
        """

        self.pattern = pattern

        if not self.configs:
            recorder('CRITICAL', 'please load manager first!')
            raise FastwebException

        self.manager = Manager()

        recorder('INFO', 'load manager start')
        with timing('s', 10) as t:
            if pattern is SyncPattern:
                self.manager.setup_sync()
            elif pattern is AsynPattern:
                # 会stop&start ioloop
                ioloop.IOLoop.current().run_sync(self.manager.setup_asyn)
        recorder('INFO', 'load manager successful -- {time}'.format(time=t))

    def load_errcode(self, errcode=None):
        """加载系统错误码

        :parameter:
          - `errcode`:自定义错误码
        """

        self.errcode = errcode if errcode else ERRCODE
        recorder('INFO', 'load errcode\n{errcode}'.format(errcode=json.dumps(self.errcode, indent=4)))
        return self.errcode


app = Loader()
