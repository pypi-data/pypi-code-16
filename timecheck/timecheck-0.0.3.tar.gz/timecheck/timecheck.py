import time


class TimeCheck:
    def __init__(self, mfile="timecheck.tc", buffer_capacity=64):
        self.mfile = mfile
        self.mbuffer = []
        self.mbuffer_capacity = buffer_capacity

    def flush(self):
        with open(self.mfile, 'a') as f:
            f.writelines(self.mbuffer)
            del self.mbuffer[:]

    def note(self, func):
        def wrapper(*args, **kwargs):
            if len(self.mbuffer) == self.mbuffer_capacity:
                self.flush()

            start_time = time.time()
            return_val = func(*args, **kwargs)
            end_time = time.time()

            self.mbuffer.append('%s,%s,%s,%s\n' %
                                (end_time, func.__module__, func.__name__,
                                (end_time - start_time) * 1000))
            return return_val
        return wrapper
