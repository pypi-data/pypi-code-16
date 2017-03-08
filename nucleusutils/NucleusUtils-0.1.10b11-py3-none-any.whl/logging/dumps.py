import logging
import os
import sys
import time
import traceback
import uuid

log = logging.getLogger('dumps')

session = str(uuid.uuid4())
_session_dumps = []

path = None


def set_dumps_path(dumps_path):
    if not os.path.isdir(dumps_path):
        os.mkdir(dumps_path)
        log.debug(f"Make dir '{dumps_path}'")
    global path
    path = dumps_path


def set_dumps_session(session_id):
    global session
    session = session_id


def get_session_dumps():
    return _session_dumps


class Dump:
    def __init__(self, name=''):
        self.name = name
        self.time = time.localtime()

        self._lines = []

        self.filename = self.get_filename()
        self.file = os.path.join(path, self.filename)

    def get_header(self):
        return [
            'Title: ' + self.name,
            'Date: ' + time.strftime("%d.%m.%Y", self.time),
            'Time: ' + time.strftime("%H:%M:%S", self.time),
            'Session: ' + session,
            ''
        ]

    def get_content(self):
        return self._lines

    def get_filename(self):
        return '{name}_{datetime}.log'.format(
            name=self.name,
            datetime=time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))

    def new_line(self, message=''):
        self._lines.append(message)

    def add_splitter(self, symbol='=', length=80):
        self.new_line(symbol * length)

    def save(self):
        # Write report
        with open(self.file, 'w') as file:
            for line in self.get_header() + self.get_content():
                file.write(line + '\r\n')
            log.debug(f"Write dump file '{self.file}'")
        _session_dumps.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Dump "{}">'.format(self.__str__())


class CrashDump(Dump):
    def __init__(self, name=''):
        super(CrashDump, self).__init__(name or 'crash')
        self.exc_type, self.exc_value, self.exc_traceback = sys.exc_info()
        self.formatted_traceback = traceback.format_exception(self.exc_type, self.exc_value, self.exc_traceback)

    def get_filename(self):
        return ('crash_' if not self.name.startswith('crash') else '') + super(CrashDump, self).get_filename()

    def get_content(self):
        return super(CrashDump, self).get_content() + [''] + self.formatted_traceback
