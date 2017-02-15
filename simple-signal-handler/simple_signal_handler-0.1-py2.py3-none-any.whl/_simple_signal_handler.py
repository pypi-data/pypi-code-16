"""The module providing the stuff for the simple_signal_handler package.
.. module:: _simple_signal_handler
  
.. moduleauthor:: Andrew Carter <andrew@invalid.com>
  
  
"""

import signal
import sys


ALL_SIGNALS = { x: getattr(signal, x)  for x in dir(signal)
               if x.startswith("SIG")
               and not x.startswith("SIG_")  # because they are just duplicates
               and not getattr(signal, x) == 0  # can register only for signals >0
               and not getattr(signal, x) == 28 # SIGWINCH [28] is sent when resizing the terminal ...
               and not x in ["SIGSTOP", "SIGKILL"]  # can't register these because you can't actually catch them (:
               }
"""dict containing collection of all possible signals that can be registered

Keys: ``str`` representations of the signals
Values: ``signal.Signal`` instance representing the signal

"""

NUMBER_TO_SIGNAL = { val: key for key, val in ALL_SIGNALS.items() }
"""inverted dictionary ALL_SIGNALS"""


class SignalWarning(RuntimeWarning):
    pass

def signal_handler(sig, frame):
    sys.exit(sig)

def register_signals(sigs = None, handler=signal_handler, verbose=1):
    """Register a signal handler for all given signals.

    Parameters
    ----------
    sigs : set-like, optional
        All signals that that should be be registered. Default: None, meaning all signals
    handler : callable, optional
        The function to be executed when a signal is caught. Default: raise a sys.exit(signal_number) 
    verbose : non-negative int, optional
        raise a warning if the signal registering failed


    """
    if sigs is None:
        sigs = set(ALL_SIGNALS)
    sigs = set(sigs)
    # register all possible signals
    for sig in ALL_SIGNALS:
        sigclass = getattr(signal, sig)
        signum = sigclass.value
        # the line below checks whether the signal has been given for
        # registering in the form of either the name, the signal class or the
        # signal number
        if set([sig, sigclass, signum]).intersection(sigs):
            try:
                signal.signal(getattr(signal, sig), signal_handler)
            except Exception as e:
                if verbose:
                    warn.warn("ignoring signal registration: [{:>2d}] {} (because {}: {!s})".format(ALL_SIGNALS[sig], sig, e.__class__.__name__, e), SignalWarning)



