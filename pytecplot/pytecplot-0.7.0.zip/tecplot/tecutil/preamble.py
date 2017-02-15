import functools
import logging

from ..exception import *


def tecutil_preamble(fn):
    """Wrapper for all calls into the TecUtil layer.

    This wrapper shows up as a decorator for all TecUtil functions. It first
    ensures a valid license is acquired and clears any previous error messages
    cached by the `_TecInterprocess` class. After calling the actual function,
    the `_tecinterprocess.last_message` object is updated and checked. Internal
    assertions will have a level of `logging.CRITICAL` and will be raised as
    `TecplotLogicError` exceptions. Other messages that normally go through
    dialogs are also checked (when `__debug__` is `True`) and errors will
    trigger an exception, but warnings and informational messages are merely
    logged (with the appropriate level).
    """
    @functools.wraps(fn)
    def _fn(self, *a, **kw):
        if __debug__:
            self.tecinterprocess._tecutil_call_count[fn.__name__] += 1
        try:
            self.tecinterprocess.clear_last_message()
            self.tecinterprocess.acquire_license()
            result = fn(self, *a, **kw)
        except TecplotInitializationError:
            raise
        except:
            lastmsg = self.tecinterprocess.update_last_message()
            if lastmsg:
                if lastmsg.level < logging.ERROR:
                    self.tecinterprocess.log_last_message()
                    raise
                else:
                    raise TecplotLogicError(lastmsg.message)
            else:
                raise
        else:
            lastmsg = self.tecinterprocess.update_last_message()
            if lastmsg:
                if lastmsg.level < logging.ERROR:
                    if __debug__:
                        self.tecinterprocess.log_last_message()
                    pass
                else:
                    raise TecplotLogicError(lastmsg.message)
        return result
    return _fn
