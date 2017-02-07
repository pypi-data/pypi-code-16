import logging
import json
import os

record_default_meanings = ('processName', 'relativeCreated', 'args', 'exc_info', 'lineno', 'msg',
                          'levelno', 'stack_info', 'module', 'process', 'pathname', 'funcName', 'levelname',
                          'thread', 'msecs', 'name', 'exc_text', 'created', 'filename', 'threadName')


class FileLogHandler(logging.Handler):
    def __init__(self, filename, mode='a'):
        super(FileLogHandler, self).__init__()
        self.baseFilename = os.path.abspath(filename)
        self.mode = mode

    def emit(self, record):
        extra_data = record.__dict__

        default_log_data = {
            'level': record.levelname,
            'message': record.msg
        }

        for keys in list(extra_data):
            for record_default_meaning in record_default_meanings:
                if keys == record_default_meaning:
                    extra_data.pop(keys)



        with open(self.baseFilename, self.mode) as file:
            file.writelines(json.dumps({'default_log_data': default_log_data, 'extra_data': extra_data}))
            file.writelines('\n')
