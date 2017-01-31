import logging
import timeit

logger = logging.getLogger(__name__)

def timed(func):
    """Timer decorator to track time of function execution.

    If logging is configured, logs (to info) the amount of time the function took
    to execute, in seconds.

    Arguments:
        func (func): A function call to be wrapped.
    """
    def wrapper(*args, **kwargs):
        """Internal func wrapper"""
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        elapsed = timeit.default_timer() - start
        logger.info('`{0}` elapsed time: {1:.2f}s'.format(func.__name__, elapsed))
        return result

    return wrapper
