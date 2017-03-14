import inspect

class MyLogger:
    """Custom logger with debug levels

    * ``self.log`` is only called if ``self.args['--log_off']`` is not set
    * ``self.o.publish`` is only called if ``self.args['--publish_off']:`` is not set

    Args:
        prefix: prefix of all log messageshostname
        channel: channel to publish to
        args: py script doctopt args
        o: self

    """

    def info(self, s):
        s = f"{get_caller()} {self.prefix} {s}"
        if not self.args['--log_off']:
            self.o.log.info(s)
        if not self.args['--publish_off']:
            self.o.publish(self.channel, s)

    def debug(self, s):
        if self.args['--debug']:
            s = f"{get_caller()} {self.prefix} {s}"
            if not self.args['--log_off']:
                self.o.log.info(s)
            if not self.args['--publish_off']:
                self.o.publish(self.channel, s)

    def error(self, s):
        s = f"{get_caller()} {self.prefix} {s}"
        self.o.log.info(s)
        self.o.publish(self.channel, s)
        print(s)

    def __init__(self, prefix, channel, args, o):
        self.prefix = prefix
        self.channel = channel
        self.o = o
        self.args = args


def get_caller():
    frm = inspect.stack()[2]
    return frm.filename
