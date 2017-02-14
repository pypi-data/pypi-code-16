import time
from threading import Thread


# class to regularly output global statistic for monitoring
class Ticker(Thread):
    def __init__(self, context, tick_interval=1):
        super().__init__()
        self.context = context
        self.tick_interval = tick_interval

    def run(self):
        while True:
            time.sleep(self.tick_interval)
            self.context.pubsub.print_info()

            # check exit condition
            if self.context.pubsub.popped >= self.context.page_limit:
                return
