import time
import threading

from proton.reactor import ApplicationEvent

from ea.messaging.handlers.logger import LoggerMixin
from ea.messaging.handlers.event import EventInjectorMixin


class HeartbeatMixin(EventInjectorMixin, LoggerMixin):
    """A mixin class for AMQP message handlers that sends periodical
    heartbeats as application events.
    """
    interval = 0.1
    beats_sent = 0

    def on_start(self, event):
        super(HeartbeatMixin, self).on_start(event)
        self.event('beat')

    def on_beat(self, event):
        self.beats_sent += 1
        self.event('heartbeat')
        t = threading.Timer(self.interval, lambda: self.event('beat'))
        t.start()
