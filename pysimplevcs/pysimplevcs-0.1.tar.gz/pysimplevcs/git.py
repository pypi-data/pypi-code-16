############################################################
#
# pysimplevcs.git
# Copyright (C) 2017, Richard Cook
# Release under MIT License
# https://github.com/rcook/pysimplevcs
#
############################################################

from __future__ import print_function
import os

from pyprelude.process import execute, proxy_command

class Git(object):
    def __init__(self, cwd=None):
        if cwd is None:
            cwd = os.getcwd()

        cwd = os.path.abspath(cwd)

        self._is_bare = execute("git", "rev-parse", "--is-bare-repository", cwd=cwd).strip() == "true"

        if self._is_bare:
            self._repo_dir = cwd
        else:
            self._repo_dir = execute("git", "rev-parse", "--show-toplevel", cwd=cwd).strip()

    @property
    def is_bare(self): return self._is_bare

    @property
    def repo_dir(self): return self._repo_dir

    def __getattr__(self, name):
        def _missing_method(*args, **kwargs):
            return proxy_command(name, self._repo_dir, lambda n, args: ["git", n] + args, *args, **kwargs)

        return _missing_method
