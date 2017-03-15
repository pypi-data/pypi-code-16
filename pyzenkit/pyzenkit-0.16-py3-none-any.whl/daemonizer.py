#!/usr/bin/python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) since 2016 Jan Mach <honza.mach.ml@gmail.com>
#                          Pavel Kacha <ph@rook.cz>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Daemonization library.
"""

import os
import re
import signal
import resource
import atexit

def get_logger_files(logger):
    """
    Return file handlers of all currently active loggers.

    Result from this method will be used during daemonization process to close
    all open file descriptors but those belonging to given logger service.

    .. warning::

        This method is hacking internal structure of different module and might
        stop working, although the related interface has been stable for a long time.
    """
    files = []
    for handler in logger.handlers:
        if hasattr(handler, 'stream') and hasattr(handler.stream, 'fileno'):
            files.append(handler.stream)
        if hasattr(handler, 'socket') and hasattr(handler.socket, 'fileno'):
            files.append(handler.socket)
    return files

def write_pid(pidfile, pid):
    """
    Write given PID into given PID file.
    """
    if not isinstance(pid, int):
        raise Exception("Process PID must be integer")
    pidfd = os.open(pidfile, os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_TRUNC)
    os.write(pidfd, bytes(str(pid)+"\n", 'UTF-8'))
    os.close(pidfd)

def read_pid(pidfile):
    """
    Read PID from given PID file.
    """
    with open(pidfile, 'r') as pidfd:
        return int(pidfd.readline().strip())

def daemonize_lite(
        chroot_dir = None, work_dir = None, umask = None, uid = None, gid = None,
        pidfile = None, signals = {}):
    """
    Perform lite daemonization of currently running process.

    The lite daemonization does everything full daemonization does but detaching
    from current session. This can be usefull when debugging daemons, because they
    can be tested, benchmarked and profiled more easily.
    """
    # Setup directories, limits, users, etc.
    if chroot_dir is not None:
        os.chdir(chroot_dir)
        os.chroot(chroot_dir)
    if umask is not None:
        os.umask(umask)
    if work_dir is not None:
        os.chdir(work_dir)
    if gid is not None:
        os.setgid(gid)
    if uid is not None:
        os.setuid(uid)

    # Setup signal handlers
    for (signum, handler) in signals.items():
        signal.signal(signum, handler)

    # Detect current process PID.
    pid = os.getpid()

    # Create PID file and ensure its removal after current process is done.
    if pidfile is not None:
        if not pidfile.endswith('.pid'):
            raise Exception("Invalid PID file name, it must end with '.pid' extension")
        write_pid(pidfile, pid)

        # Define and setup 'atexit' closure, that will take care of removing pid file
        @atexit.register
        def unlink_pidfile():
            try:
                os.unlink(pidfile)
            except Exception:
                pass
        return (pid, pidfile)
    else:
        return (pid, None)

def daemonize(
        chroot_dir = None, work_dir = None, umask = None, uid = None, gid = None,
        pidfile = None, files_preserve = [], signals = {}):
    """
    Perform full daemonization of currently running process.

    NOTE: It would be possible to call daemonize_lite() method from within this
    method, howewer for readability purposes and to maintain correct ordering
    of the daemonization steps I decided against coding best practices and kept
    two separate methods with similar contents. It will be necessary to update
    both when making any improvements, however I do not expect them to change
    much and often, if ever.
    """
    # Setup directories, limits, users, etc.
    if chroot_dir is not None:
        os.chdir(chroot_dir)
        os.chroot(chroot_dir)
    if umask is not None:
        os.umask(umask)
    if work_dir is not None:
        os.chdir(work_dir)
    if uid is not None:
        os.setuid(uid)
    if gid is not None:
        os.setgid(gid)

    # Doublefork and split session.
    if os.fork()>0:
        os._exit(0)
    os.setsid()
    if os.fork()>0:
        os._exit(0)

    # Setup signal handlers
    for (signum, handler) in signals.items():
        signal.signal(signum, handler)

    # Close all open file descriptors.
    #descr_preserve = set(f.fileno() for f in files_preserve)
    #maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    #if maxfd==resource.RLIM_INFINITY:
    #    maxfd = 65535
    #for fd in range(maxfd, 3, -1):  # 3 means omit stdin, stdout, stderr
    #    if fd not in descr_preserve:
    #        try:
    #            os.close(fd)
    #        except Exception:
    #            pass

    # Redirect stdin, stdout, stderr to /dev/null.
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in range(3):
        os.dup2(devnull, fd)

    # Detect current process PID.
    pid = os.getpid()

    # Create PID file and ensure its removal after current process is done.
    if pidfile is not None:
        if not pidfile.endswith('.pid'):
            raise Exception("Invalid PID file name, it must end with '.pid' extension")
        write_pid(pidfile, pid)

        # Define and setup atexit closure
        @atexit.register
        def unlink_pidfile():
            try:
                os.unlink(pidfile)
            except Exception:
                pass
        return (pid, pidfile)
    else:
        return (pid, None)

if __name__ == "__main__":
    """
    Perform the demonstration.
    """

    def hnd_sig_hup(signum, frame):
        print("Received signal HUP")
    def hnd_sig_usr1(signum, frame):
        print("Received signal USR1")
    def hnd_sig_usr2(signum, frame):
        print("Received signal USR2")

    (pid, pidfile) = daemonize_lite(
            work_dir = "/tmp",
            pidfile = "/tmp/demo.pyzenkit.daemonizer.pid",
            signals = {
                signal.SIGHUP:  hnd_sig_hup,
                signal.SIGUSR1: hnd_sig_usr1,
                signal.SIGUSR2: hnd_sig_usr2,
            }
        )

    print("Lite daemonization complete:")
    print("\tPID: '{}'".format(pid))
    print("\tPID file: '{}'".format(pidfile))
    print("\tCWD: '{}'".format(os.getcwd()))
    print("\tPID in PID file: '{}'".format(read_pid(pidfile)))

    print("Checking signal handling:")
    os.kill(pid, signal.SIGHUP)
    os.kill(pid, signal.SIGUSR1)
    os.kill(pid, signal.SIGUSR2)
    os.kill(read_pid(pidfile), signal.SIGHUP)
    os.kill(read_pid(pidfile), signal.SIGUSR1)
    os.kill(read_pid(pidfile), signal.SIGUSR2)
