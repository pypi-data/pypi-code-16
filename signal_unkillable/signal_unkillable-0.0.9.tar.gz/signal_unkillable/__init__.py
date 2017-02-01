import sys, os, subprocess


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def activate(pid=None):
    if pid is None:
        pid = os.getpid()
    module = os.path.join(THIS_DIR, 'signal_unkillable.ko')
    os.system("sudo rmmod signal_unkillable")
    os.system("sudo insmod '%s' pid=%d" % (module, pid))
