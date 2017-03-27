import time
from contextlib import contextmanager
from termcolor import cprint, colored
from qlib.log import LogControl
from qlib.io import input_default
from ._pipe import stdout

_do_some = lambda x: cprint("%s ..." % x, "yellow", end="")
_ok = lambda : cprint("\b\b\b ok", "green", attrs=['bold'])
_err = lambda : cprint("\b\b\b err", "red", attrs=['bold'])


@contextmanager
def just_info(info):
    try:
        _do_some(info)
        with stdout(None):
            yield
    except:
        _err()
    else:
        _ok()




def dict_cmd(dic):

    """
    for every dict do a interact input.
    """
    def _input(name):
        return input_default("[%s]: " %  colored(name,'red', attrs=['bold']), "Uknow")

    m = dic
    with LogControl.jump(LogControl.SIZE[0] - 1, 0):
        print("=" * LogControl.SIZE[1])
        for k in dic:
            v = _input(k)
            if v == "*None*":
                continue
            m[k] = v
        return m
