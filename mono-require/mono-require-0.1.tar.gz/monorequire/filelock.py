# coding: utf8

import os
import errno
import time

from os import path


class LockTimeoutException(Exception):
    def __init__(self, resource, timeout):
        self.resource = resource
        self.timeout = timeout

    def __repr__(self):
        return f"try open lock file {self.resource} timeout. time: {self.timeout}"


class FileLock:
    def __init__(
            self, resource, mode, buffering,
            encoding, errors, newline, timeout,
            delay, lock_path
    ):
        self.resource = resource
        self.lock = path.join(
            self.get_lock_path(lock_path),
            f".{path.basename(resource)}.lock"
        )
        self.timeout = timeout
        self.delay = delay
        self.open_args = dict(
            mode=mode,
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline
        )

    def get_lock_path(self, lock_path):
        if lock_path == ".":
            return path.dirname(path.realpath(self.resource))
        else:
            return path.realpath(lock_path)


    def __enter__(self):
        waiting_time = 0
        while True:
            try:
                self.lock_fd = os.open(
                    self.lock, os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise e
                waiting_time += self.delay
                if waiting_time > self.timeout:
                    raise LockTimeoutException(
                        self.resource, self.timeout
                    )
                time.sleep(self.delay)
        self.fd = open(self.resource, **self.open_args)
        return self.fd

    def __exit__(self, type, value, traceback):
        os.close(self.lock_fd)
        os.unlink(self.lock)
