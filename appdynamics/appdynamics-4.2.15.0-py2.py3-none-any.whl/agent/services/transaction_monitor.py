import logging
import threading
import time

from appdynamics import config


class TransactionMonitorService(threading.Thread):
    MONITOR_PERIOD = 10

    def __init__(self, active_bts):
        super(TransactionMonitorService, self).__init__()
        self.active_bts = active_bts
        self.logger = logging.getLogger('appdynamics.agent')
        self.running = False
        self.name = 'TransactionMonitorService'
        self.daemon = True

    def _is_running(self):
        return self.running

    def run(self):
        self.running = True
        while self._is_running():
            for bt in self.active_bts.copy():
                if bt.timer.duration_ms > config.BT_MAX_DURATION_MS:
                    # Remove the BT from active bts but do not try to report it.
                    #  This implicitly deletes it from current_bts as well
                    self.active_bts.discard(bt)
                    self.logger.warning('BT:%s (%s) took too long. Ended prematurely by the Transaction Monitor.' %
                                        (bt.request_id, bt.name))

            time.sleep(self.MONITOR_PERIOD)
