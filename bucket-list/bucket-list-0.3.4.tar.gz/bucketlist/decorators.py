import time

from bucketlist import logger


def dumptime(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        logger.info('%2.2f sec %s.%s.%s' % (te-ts, method.__module__, method.__class__.__name__, method.__name__))
        return result

    return timed
