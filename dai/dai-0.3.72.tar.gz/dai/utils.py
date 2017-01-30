import time

def rate_limited(period, damping=1.0, important=True):
  '''
  originally from https://github.com/tomasbasham/ratelimit

  Prevent a method from being called
  if it was previously called before
  a time widows has elapsed.
  :param period: The time window after which method invocations can continue.
  :param damping: A factor by which to dampen the time window.
  :return function: Decorated function that will forward method invocations if the time window has elapsed.
  '''
  frequency = damping / float(period)
  def decorate(func):
    last_called = [0.0]
    def func_wrapper(*args, **kargs):
      elapsed = time.clock() - last_called[0]
      left_to_wait = frequency - elapsed
      if left_to_wait > 0:
        if important:
            time.sleep(left_to_wait)
        else:
            return None
      ret = func(*args, **kargs)
      last_called[0] = time.clock()
      return ret
    return func_wrapper
  return decorate

class Metrics():

    def __init__(self, value, unit=''):
        self.value = value
        self.unit = unit
        self.__repr__ = self.__str__

    def __str__(self):
        return "{}{}".format(self.value, self.unit)

class NonBlockingStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''
        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while True:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    self.end = True
                    break
                    #raise UnexpectedEndOfStream
                time.sleep(0.01)
        self.end = False
        self._t = threading.Thread(target=_populateQueue,
                                   args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    def readline(self, timeout=None):
        try:
            return self._q.get(block=timeout is not None,
                               timeout=timeout)
        except Empty:
            if self.end:
                raise UnexpectedEndOfStream
            return None

class UnexpectedEndOfStream(Exception):
    pass
