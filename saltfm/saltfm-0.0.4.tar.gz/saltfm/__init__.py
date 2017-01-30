#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Salt Formula Manager
https://github.com/saltstack-formulas
"""
import os
import subprocess
from subprocess import Popen
import saltfm.exceptions as ex
from saltfm.log import logger
from saltfm.config import config

_root_dir = os.path.abspath(config['root_dir'])
CACHE_DIR = os.path.join(_root_dir, "var/cache/saltfm/")
SALT_ROOT = os.path.join(_root_dir, "srv/salt/saltfm")


def setup_dirs():
    # TODO(pythonize)
    Popen(["mkdir", "-p", CACHE_DIR])
    Popen(["mkdir", "-p", SALT_ROOT])


def get_repo_name(repo):
    return os.path.basename(repo)


def get_local_repo_path(repo):
    return os.path.join(CACHE_DIR, get_repo_name(repo))


def normalize_repo(entered):
    if not entered.startswith(('http', 'git')):
        if '.' in entered:
            entered = entered.replace('.', '/')
        else:
            entered = 'saltstack-formulas/{0}-formula'.format(entered)
        return 'https://github.com/{0}'.format(entered)
    else:
        return entered


def download(repo, version='master', formulas=None):
    setup_dirs()
    repo = normalize_repo(repo)

    local_repo = get_local_repo_path(repo)

    if os.path.isdir(local_repo) and len(os.listdir(local_repo)) > 0:
        logger.info("Repo %s exists and not empty", local_repo)
        # TODO(check branch version)
        return True

    process = Popen(["git", "clone", "--depth=1", repo, local_repo],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                    )
    out, err = process.communicate()
    if process.returncode != 0:
        raise ex.DownloadException(err + str(process.returncode))
    logger.info("Downloaded %s", repo)
    # TODO check only formulas dir into saltfm

    return True


def setup(repo, formulas):
    if formulas is None or len(formulas) == 0:
        formulas = [get_repo_name(repo).replace('-formula', '')]

    assert isinstance(formulas, list)
    for f in formulas:
        target = os.path.join(SALT_ROOT, f)
        if os.path.islink(target):
            # TODO check if is manglelink
            pass
        src = os.path.join(get_local_repo_path(repo), f)
        try:
            os.symlink(src, target)
        except Exception as e:
            # TODO
            print e
        logger.info("Got formula %s ---> %s", src, target)


def install(repo, version='master', formulas=None):
    download(repo, version, formulas)
    setup(repo, formulas)


def test():
    download("https://github.com/saltstack-formulas/jenkins-formula")


if __name__ == "__main__":
    test()
