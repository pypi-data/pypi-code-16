# -*- coding: utf-8 -*-
import os
import tarfile
import hashlib

from ..config import config as app_conf


def md5sum_dir(dirname, tar_file_path=app_conf.lock.tar_file_path):
    """MD5 hash a directory by first creating a `tar` and hashing the tar."""
    if not os.path.isdir(dirname):
        raise TypeError('"%s" is not a directory' % dirname)

    with tarfile.open(tar_file_path, 'w') as tar:
        tar.add(dirname, arcname=os.path.basename(dirname))

    hash_md5 = hashlib.md5()
    with open(tar_file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    try:
        os.remove(tar_file_path)
    except OSError:
        pass
    return hash_md5.hexdigest()


def read_lock(lock_file_path=app_conf.lock.lock_file_path):
    try:
        with open(lock_file_path, 'rU') as f:
            return f.readline().strip('\n')
    except IOError:
        return None


def write_lock(dirname, lock_file_path=app_conf.lock.lock_file_path):
    with open(lock_file_path, 'w') as f:
        f.write(md5sum_dir(dirname))
