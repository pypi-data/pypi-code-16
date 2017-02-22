from logging import Handler


class DBHandler(Handler, object):

    def emit(self, record):
        from .models import LogEntry, LogTag
        log_entry = LogEntry.objects.create(level=record.levelname, message=record.msg)

        if record.args:
            for tag in record.args[0]:
                log_tag = LogTag.objects.get_or_create(tag=tag)
                log_tag[0].log_entries.add(log_entry)
