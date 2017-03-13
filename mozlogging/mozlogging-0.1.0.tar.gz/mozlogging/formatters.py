import copy
import json
import logging

MOZLOG_ENVVERSION = '2.0'


class MozLogFormatter(logging.Formatter):
    """A mozlog logging formatter."""

    # Syslog severity levels.
    SYSLOG_EMERG = 0  # system is unusable
    SYSLOG_ALERT = 1  # action must be taken immediately
    SYSLOG_CRIT = 2  # critical conditions
    SYSLOG_ERR = 3  # error conditions
    SYSLOG_WARNING = 4  # warning conditions
    SYSLOG_NOTICE = 5  # normal but significant condition
    SYSLOG_INFO = 6  # informational
    SYSLOG_DEBUG = 7  # debug-level messages

    # Mapping from python logging priority to Syslog severity level.
    priority_map = {
        "DEBUG": SYSLOG_DEBUG,
        "INFO": SYSLOG_INFO,
        "WARNING": SYSLOG_WARNING,
        "ERROR": SYSLOG_ERR,
        "CRITICAL": SYSLOG_CRIT,
    }

    def serialize(self, mozlog_record):
        """Serialize a mozlog record."""
        return json.dumps(mozlog_record, sort_keys=True)

    def format(self, record):
        """Formats a log record and serializes to mozlog json"""
        mozlog_record = {
            # TODO: Add the Hostname.
            # 'Hostname': 'server-a123.mozilla.org',
            'Type': 'app.log',
            'EnvVersion': MOZLOG_ENVVERSION,
        }
        mozlog_record['Timestamp'] = int(record.created * 1000000000)
        mozlog_record['Logger'] = record.name
        mozlog_record['Severity'] = self.priority_map.get(
            record.levelname, self.SYSLOG_WARNING
        )

        for arg in record.args:
            overrides = arg if isinstance(arg, dict) else {'Type': arg}
            mozlog_record.update(overrides)

        mozlog_record['Fields'] = (
            copy.copy(record.msg) if isinstance(record.msg, dict) else {
                'msg': record.msg
            }
        )

        if record.exc_info:
            mozlog_record['Fields']['exc_info'] = (
                self.formatException(record.exc_info)
            )

        return self.serialize(mozlog_record)


class PrettyMozLogFormatter(MozLogFormatter):
    """A mozlog logging formatter which pretty prints."""

    def serialize(self, mozlog_record):
        """Serialize a mozlog record."""
        return json.dumps(mozlog_record, sort_keys=True, indent=4)
