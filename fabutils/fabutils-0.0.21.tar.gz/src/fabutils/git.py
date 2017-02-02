# -*- coding: utf-8 -*-
"""
git related helpers.
"""
from __future__ import absolute_import
from fabric.api import local, quiet


def get_changed_files():
    """ Get a list of unstaged changes in the current repo. """
    with quiet():
        gitcmd = ' '.join((
            "git status --porcelain",
            "| sed '/.*\.py/!d'",       # Leave only .py files
            "| sed '/^test_.*\.py/d'",  # Remove all test_*.py files
            "| awk '{print $2;}'",
        ))

        return local(gitcmd, capture=True).splitlines()


def get_staged_files():
    """ Get a list of files staged for commit in the current repo. """
    with quiet():
        gitcmd = ' '.join((
            "git diff --cached --name-only",
            "| sed '/.*\.py/!d'",       # Leave only .py files
            "| sed '/^test_.*\.py/d'",  # Remove all test_*.py files
        ))

        return local(gitcmd, capture=True).splitlines()
