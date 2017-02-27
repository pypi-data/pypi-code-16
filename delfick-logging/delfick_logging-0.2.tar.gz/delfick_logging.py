from rainbow_logging_handler import RainbowLoggingHandler
import logging.handlers
import logging
import json
import sys
import os

class SimpleFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        if "ignore_extra" in kwargs:
            ignore_extra = kwargs.pop("ignore_extra")
        else:
            ignore_extra = False
        super(SimpleFormatter, self).__init__(*args, **kwargs)
        self.ignore_extra = ignore_extra

    def format(self, record):
        if self.ignore_extra:
            record.message = record.getMessage()
            return self.formatMessage(record)
        else:
            return super(SimpleFormatter, self).format(record)

class SyslogHandler(logging.handlers.SysLogHandler):
    def format(self, record):
        oldGetMessage = record.getMessage

        def newGetMessage():
            def f(v):
                if isinstance(v, dict):
                    return json.dumps(v, default=f, sort_keys=True)
                elif hasattr(v, "as_dict"):
                    return json.dumps(v.as_dict(), default=f, sort_keys=True)
                elif isinstance(v, str):
                    return v
                else:
                    return repr(v)

            if isinstance(record.msg, dict):
                base = record.msg
            else:
                base = {"msg": oldGetMessage()}

            dc = record.__dict__
            for attr in ("name", "levelname"):
                if dc.get(attr):
                    base[attr] = dc[attr]

            if dc.get("exc_info"):
                base["traceback"] = self.formatter.formatException(dc["exc_info"])

            if dc.get("stack_info"):
                base["stack"] = self.formatter.formatStack(dc["stack_info"])

            return f(base)
        record.getMessage = newGetMessage
        return super(SyslogHandler, self).format(record)

class RainbowHandler(RainbowLoggingHandler):
    def format(s, record):
        oldGetMessage = record.getMessage

        def newGetMessage():
            def f(v):
                def reperer(o):
                    return repr(o)
                if type(v) is dict:
                    return json.dumps(v, default=reperer, sort_keys=True)
                elif hasattr(v, "as_dict"):
                    return json.dumps(v.as_dict(), default=reperer, sort_keys=True)
                else:
                    return v

            if type(record.msg) is dict:
                s = []
                if record.msg.get("msg"):
                    s.append(record.msg["msg"])
                for k, v in sorted(record.msg.items()):
                    if k != "msg":
                        s.append("{}={}".format(k, f(v)))
                return "\t".join(s)
            else:
                return oldGetMessage()
        record.getMessage = newGetMessage
        return super(RainbowHandler, s).format(record)

class LogContext(object):
    def __init__(self, initial=None, extra=None):
        self.initial = initial if initial is not None else {}
        self.context = dict(self.initial)
        if extra:
            for k, v in extra.items():
                self.context[k] = v

    def __call__(self, *args, **kwargs):
        res = dict(self.context)
        if args:
            res["msg"] = " ".join(args)
        for k, v in kwargs.items():
            res[k] = v
        return res

    def using(self, **kwargs):
        return LogContext(self.context, kwargs)

lc = LogContext()

def setup_logging(log=None, level=logging.INFO, syslog="", syslog_address="", only_message=False, logging_handler_file=sys.stderr):
    """
    Setup the logging handlers

    log
        The log to add the handler to.

        * If this is a string we do logging.getLogger(log)
        * If this is None, we do logging.getLogger("")
        * Otherwise we use as is

    level
        The level we set the logging to

    syslog
        The syslog program name to use, this also turns on syslog logging instead
        of console logging.

    syslog_address
        The address to send syslog logs to. If this is a falsey value, then the
        default is used.

    only_message
        Whether to only print out the message when going to the console

    logging_handler_file
        The file to print to when going to the console
    """
    log = log if log is not None else logging.getLogger(log)

    if syslog:
        opts = {}
        if syslog_address:
            opts = {"address": syslog_address}
        handler = SyslogHandler(**opts)
    else:
        handler = RainbowHandler(logging_handler_file)

    # Protect against this being called multiple times
    handler.delfick_logging = True
    if any(getattr(h, "delfick_logging", False) for h in log.handlers):
        return

    base_format = "%(name)-15s %(message)s"
    if only_message or syslog:
        base_format = "%(message)s"

    if syslog:
        handler.setFormatter(SimpleFormatter("{0}[{1}]: {2}".format(syslog, os.getpid(), base_format), ignore_extra=True))
    else:
        handler._column_color['%(asctime)s'] = ('cyan', None, False)
        handler._column_color['%(levelname)-7s'] = ('green', None, False)
        handler._column_color['%(message)s'][logging.INFO] = ('blue', None, False)
        if only_message:
            handler.setFormatter(SimpleFormatter(base_format))
        else:
            handler.setFormatter(SimpleFormatter("{0} {1}".format("%(asctime)s %(levelname)-7s", base_format)))

    log.addHandler(handler)
    log.setLevel(level)
    return handler

def setup_logging_theme(handler, colors="light"):
    """
    Setup a logging theme

    Currently there is only ``light`` and ``dark`` which consists of a difference
    in color for INFO level messages.
    """
    if colors not in ("light", "dark"):
        logging.getLogger("delfick_logging").warning(
              lc( "Told to set colors to a theme we don't have"
                , got=colors
                , have=["light", "dark"]
                )
            )
        return

    # Haven't put much effort into actually working out more than just the message colour
    if colors == "light":
        handler._column_color['%(message)s'][logging.INFO] = ('cyan', None, False)
    else:
        handler._column_color['%(message)s'][logging.INFO] = ('blue', None, False)
