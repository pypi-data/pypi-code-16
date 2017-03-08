from __future__ import absolute_import

from logstash.formatter import LogstashFormatterVersion1


class Formatter(LogstashFormatterVersion1):

    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'host': self.host,
            'pathname': record.pathname,
            'tags2': self.tags,
            'message': record.getMessage(),
            # Extra Fields
            'level': record.levelname,
            'logger_name': record.name,
            'extra': {str(k): str(v) for k, v in self.get_extra_fields(record)}
        }

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)
