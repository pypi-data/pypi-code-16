# -*- coding: utf-8 -*-

import logging
import os
import sys
import datetime


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


class Logger(object):

    def __init__(self, name):
        self.path = os.path.dirname(os.path.realpath(__file__))
        self.date = str(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.name = name

        self.setup('logs', is_dir=True)
        self.setup('logs\\' + self.name + '_' + self.date + '_log.log', is_file=True)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        self.log_handle = logging.FileHandler('logs\\' + self.name + '_' + self.date + '_log.log')
        self.log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handle.setFormatter(self.log_formatter)
        self.logger.addHandler(self.log_handle)

        self.current_running_log = {}


    @staticmethod
    def get_current_data_stamp():
        return str(datetime.datetime.now().strftime("%Y-%m-%d"))

    @staticmethod
    def setup(path, is_file=False, is_dir=False):
        if is_dir == True:
            if os.path.exists(path):
                pass
            else:
                os.mkdir(path)
        elif is_file == True:
            if os.path.isfile(path):
                os.system('del /s /q ' + path)
                with open(path, 'w')as f:
                    f.close()
            else:
                with open(path, 'w')as f:
                    f.close()

    def set_log_level(self, level):
        self.log_handle.setLevel(level)

    def write_log_file(self, _log):
        log_dict = _log

        for key, value in log_dict.items():
            try:
                if key == 'error':
                    for item in value:
                        self.set_log_level(LEVELS['error'])
                        self.logger.error(str(item))

                if key == 'debug':
                    for item in value:
                        self.set_log_level(LEVELS['debug'])
                        self.logger.debug(str(item))

                if key == 'warning':
                    for item in value:
                        self.set_log_level(LEVELS['warning'])
                        self.logger.warning(str(item))

                if key == 'info':
                    for item in value:
                        self.set_log_level(LEVELS['info'])
                        self.logger.info(str(item))

                if key == 'critical':
                    for item in value:
                        self.set_log_level(LEVELS['critical'])
                        self.logger.critical(str(item))

            except Exception as e:
                self.set_log_level(LEVELS['debug'])
                self.logger.debug(' :: Exception has occurred => ' + str(e))



