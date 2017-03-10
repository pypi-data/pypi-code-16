

class PollMixIn(object):

    def poll(self):
        """
        Override this to poll for changes
        polls every 100 msec
        """
        pass

    def _poll(self):
        try:
            self.polling_interval

        except Exception:
            self.polling_interval = 100

        self.poll()
        self.after(self.polling_interval, self._poll)
