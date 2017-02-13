"""Utilities for use in tools.

"""

import logging
import re
from contextlib import contextmanager

log = logging.getLogger(__name__)

OK = {
    'status': 'ok'
}

FAIL = {
    'status': 'fail'
}

NOTHING_TO_DO = {
    'status': 'nothing_to_do'
}

NON_WORD_PATTERN = re.compile(r'\W')


@contextmanager
def package_script(resource_path, resource_package="menhir"):
    """Execute a block of code with the given script from the package.

    Yields a file like object that is the script written onto the filesystem.
    """
    import tempfile
    import pkg_resources
    import stat
    from os import chmod, remove

    script = pkg_resources.resource_string(resource_package, resource_path)
    fname = None
    try:
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            fname = f.name
            f.write(script)
        chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        yield f
    finally:
        remove(fname)


@contextmanager
def working_dir(path):
    """Execute a block of code within the given working dir."""
    import os
    dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(dir)


def tool_env():
    """Return the default tool environment dict."""
    import os
    import os.path

    default_pyenv_root = os.path.join(os.getenv("HOME"), ".pyenv")
    env = {
        "HOME": os.getenv("HOME"),
        "PATH": os.getenv("PATH"),
        "PYENV_ROOT": os.getenv("PYENV_ROOT", default_pyenv_root),
    }

    v = os.getenv("AWS_DEFAULT_REGION")
    if v:
        env["AWS_DEFAULT_REGION"] = v

    v = os.getenv("LANG")
    if v:
        env["LANG"] = v

    v = os.getenv("LC_ALL")
    if v:
        env["LC_ALL"] = v

    v = os.getenv("DEBUG")
    if v:
        env["DEBUG"] = v

    return env


def call(cmd, *args, **kwargs):
    """Call a subprocess, returning a menhir result."""
    import subprocess
    res = subprocess.call(cmd, *args, **kwargs)
    if res:
        return FAIL
    return OK


def slugify(s, length=None, replace=NON_WORD_PATTERN):
    s = re.sub(replace, "_", s)
    if length:
        s = s[:length]
    return s


@contextmanager
def run_if(cond, phase_name, path):
    if cond:
        log.info(
            'Running %(phase)s in %(path)s',
            {'phase': phase_name, 'path': path}
        )
        yield True
    else:
        yield False
        log.info(
            'Not running %(phase)s in %(path)s',
            {'phase': phase_name, 'path': path}
        )
