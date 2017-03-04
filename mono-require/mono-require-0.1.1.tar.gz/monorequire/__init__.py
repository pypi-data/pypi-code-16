# coding: utf8

from .filelock import FileLock


def require(
      resource, mode='r+', buffering=-1,
      encoding=None, errors=None, newline=None,
      timeout=1, delay=0.001, lock_path="."
):
    return FileLock(
        resource, mode, buffering,
        encoding, errors, newline,
        timeout, delay, lock_path
    )
