import time

from logging import FileHandler, makeLogRecord
from threatconnect.RequestObject import RequestObject
from json import dumps


def create_log_entry(record):
    log_entry = {}

    if hasattr(record, 'created'):
        log_entry['timestamp'] = record.created

    if hasattr(record, 'msg'):
        log_entry['message'] = record.msg

    if hasattr(record, 'levelname'):
        log_entry['level'] = record.levelname

    return log_entry


class ApiLoggingHandler(FileHandler):
    """ Extension of FileHandler; used to send log entries to the api """

    def __init__(self, filename, tc, max_entries_before_flush=100):
        super(ApiLoggingHandler, self).__init__(filename)
        self.tc = tc
        self.entries = []
        self.max_entries_before_flush = max_entries_before_flush

    def emit(self, record):
        entry = create_log_entry(record)

        # if we've reached the max_entries threshold, flush the handler
        if len(self.entries) > self.max_entries_before_flush:
            self.log_to_api()
            self.entries = []

        self.entries.append(entry)
        super(ApiLoggingHandler, self).emit(record)

    def log_to_api(self):
        if len(self.entries) > 0:
            # make api call
            ro = RequestObject()
            ro.set_http_method('POST')
            ro.set_owner_allowed(True)
            ro.set_resource_pagination(False)
            ro.set_request_uri('/v2/logs/app')
            ro.set_body(dumps(self.entries))

            # retrieve and display the results; don't log during api request so we don't end up with duplicate info
            try:
                self.tc.api_request(ro, log=False)
            except RuntimeError as re:
                # can't really do anything if it fails
                error_data = {'levelname': 'ERROR',
                              'created': time.time(),
                              'msg': 'API LOGGING FAILURE -- Unable to send log entries to api: {}'.format(self.entries)}
                lr = makeLogRecord(error_data)
                self.entries = []
                self.emit(lr)

            self.entries = []