# -*- coding: utf-8 -*-
"""
Common part for linting commands.
"""
from __future__ import absolute_import
from fabric.api import local, quiet
from six import string_types
from .util import infomsg, sysmsg, errmsg


class LintError(RuntimeError):
    """ Raised when there were problems with linting the code.

    This is not about the code not passing the linting, but when there are
    problems with running the linters themselves.
    """
    pass


def surround_paths_with_quotes(paths):
    """ Put quotes around all paths and join them with space in between. """
    if isinstance(paths, string_types):
        raise ValueError(
            "paths cannot be a string. Use array with one element instead."
        )
    return ' '.join('"' + path + '"' for path in paths)


def is_pep8_compliant(paths):
    """ Check the given paths against PEP8.

    This will run the ``pep8`` tool, so any existing configuration for it will
    be used.
    """
    sysmsg("Checking PEP8 compatibility")

    paths = surround_paths_with_quotes(paths)

    with quiet():
        out = local('pep8 {}'.format(paths), capture=True)
        output = out.strip()
        if output:
            print(output)

    if out.return_code != 0:
        errmsg("pep8 failed with return code {}".format(out.return_code))

    return out.return_code == 0


def is_pylint_compliant(paths):
    """ Check the given paths pylint.

    This will run ``pylint`` tool and use ``setup.cfg`` as the configuration
    file.
    """
    sysmsg("Running static code analysis")

    paths = surround_paths_with_quotes(paths)

    with quiet():
        out = local('pylint --rcfile setup.cfg {}'.format(paths), capture=True)
        output = out.strip()
        if output:
            print(output)

    if out.return_code != 0:
        errmsg("pylint failed with return code {}".format(out.return_code))

    return out.return_code == 0


def lint_files(paths):
    """ Run static analysis on the given files.

    :param paths:   Iterable with each item being path that should be linted..
    """
    sysmsg("Linting project files")
    if isinstance(paths, string_types):
        raise ValueError(
            "paths cannot be a string. Use array with one element instead."
        )

    paths = list(paths)

    infomsg("Will check the following paths:")
    for path in paths:
        print("--   {}".format(path))

    if len(paths) == 0:
        raise LintError("No files to lint")

    return all((
        is_pep8_compliant(paths),
        is_pylint_compliant(paths),
    ))
