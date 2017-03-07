"""wracker - the Python wheel rack.

A Python version of Bundler.

Currently in early alpha, under development.

WRACKER_DIR can be set by the environment, and defaults to ~/.wracker

* Installs packages to $WRACKER_DIR/packages

* Installs "clean" virtualenvs to $WRACKER_DIR/envs

    This is done to prevent globally installed packages from leaking into the
    user's scope.  One env per Python version
"""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import argparse
import collections
import json
import os.path
import re
import shutil
import subprocess
import sys

import pkg_resources

from .__version__ import __version__
from . import entrypoints
from .requirement_parser import Requirement
from .util import prepend_path, temp_dir, try_makedirs
from .which import which


INPUT_FILE = 'requirements.in'
FROZEN_FILE = 'requirements.txt'
WRACKER_DIR = os.environ.get(
    'WRACKER_DIR', os.path.join(os.path.expanduser("~"), '.wracker'))
PYTHON = 'python'


def die(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    print(*args, **kwargs)
    sys.exit(1)


def look_up_for_file_or_die(filename):
    """Look in PWD or parent dirs for filename.

    Returns path of the first dir found that contains filename.
    """
    curr_path = os.getcwd()
    try_count = 0
    while (os.path.exists(curr_path)
           and not os.path.exists(os.path.join(curr_path, filename))
           and try_count <= 25):
        try_count += 1
        curr_path = os.path.dirname(curr_path)

    if not os.path.exists(os.path.join(curr_path, filename)):
        die("Error: No '{}' file found.".format(filename))
    return curr_path


def install_dist(platform, requirement):
    """Install a package by name."""
    with temp_dir() as tmp_dir:
        subprocess.check_call([
            PYTHON, '-m', 'pip.__main__', 'install', '--no-deps',
            '--target', tmp_dir,
            str(requirement)])

        dists = list(pkg_resources.find_distributions(tmp_dir))
        assert len(dists) == 1, \
            "Need exactly one distribution: " + str(dists)
        dist = dists[0]
        target = python_path_for(platform, dist.as_requirement())

        # If try_makedirs() is False, the package is probably already
        # installed. Attempting to overwrite it might cause errors, so just
        # leave it alone.
        if try_makedirs(target):
            try:

                # entrypoints MUST be installed before the dist is installed!!
                # Otherwise attempts to inspect dist will fail.
                entrypoints.install_for(platform, dist)

                for item in os.listdir(tmp_dir):
                    shutil.move(os.path.join(tmp_dir, item), target)
            except Exception:
                # Install failed - remove target dir
                shutil.rmtree(target)
                raise

    # Find the local dist
    dists = list(pkg_resources.find_distributions(target))
    assert len(dists) == 1
    assert str(dists[0].as_requirement()) == str(dist.as_requirement())
    return dists[0]


def local_path_for(platform, requirement):
    impl_tag = '{python_implementation}{python_version}'.format(**platform)
    pkg_name = requirement.key
    pkg_version = requirement.specs[0][1]
    return os.path.join(
        WRACKER_DIR, 'packages', impl_tag, pkg_name, pkg_version)


def python_path_for(platform, requirement):
    return os.path.join(local_path_for(platform, requirement), 'site-packages')


def is_installed(platform, requirement):
    try:
        if requirement.specs[0][0] != '==':
            return False
    except IndexError:
        return False
    return os.path.exists(python_path_for(platform, requirement))


def get_dist(platform, requirement):
    """Get the given requirement, installing it if necessary."""
    if is_installed(platform, requirement):
        dists = list(
            pkg_resources.find_distributions(python_path_for(
                platform, requirement)))
        assert len(dists) == 1
        assert str(dists[0].as_requirement()) == str(requirement), \
            "{}, {}".format(dists, requirement)
        return dists[0]
    else:
        return install_dist(platform, requirement)


def ensure_packages(requirements, locks, platform):
    """Install all packages in `requirements`.

    Recursively installs dependencies.

    Platform is a dict as returned by get_platform_info(), and is used for
    environment checks.

    Yields a list of all Distribution objects installed this way.
    """
    packages_to_install = list(requirements.keys())

    # packages_to_install may change during runtime (e.g. if a new requirement
    # requires other new requirements)
    installed = set()
    i = 0
    while i < len(packages_to_install):
        package = packages_to_install[i]
        target = locks.get(package, requirements[package])
        if not target.is_needed_for(platform):
            print("Ignoring requirement", target, "on this platform.",
                  file=sys.stderr)
        dist = get_dist(platform, target)
        installed.add(dist)

        # Update locks... if two packages require the same thing, it needs to be
        # locked to the same version
        locks[dist.key] = Requirement(dist.as_requirement())

        # Make sure dependencies get installed as well
        extra_requirements = dist.requires()
        for r in extra_requirements:

            # Let user's preference overrule library's preference.
            # TODO: probably need to do some conflict checks here...
            req = Requirement(r)
            if req.is_needed_for(platform):
                if not r.key in requirements:
                    packages_to_install.append(r.key)
                requirements.setdefault(r.key, req)
        i += 1
    return installed


def write_frozen(project_dir, installed_pkgs):
    """Write the frozen file.

    installed_packages is a list of Requirement instances.
    """
    installed_strs = sorted(str(req) for req in installed_pkgs)
    with open(os.path.join(project_dir, FROZEN_FILE), 'w') as outfile:
        for installed in installed_strs:
            print(installed, file=outfile)


def get_python_version():
    """Get the version of Python on the PATH."""
    return subprocess.check_output(
        [PYTHON, '--version'], stderr=subprocess.STDOUT).strip()


def get_python_major_minor_version():
    """Get e.g. '3.5' for Python 3.5"""

    # Only tested on CPython
    version = get_python_version()
    match = re.search(r'\b(\d\.\d)(?:\.\d)?\b', version)
    assert match
    return match.group(1)


def get_env_dir():
    """Get a Wracker path to a clean env for python."""
    python_version = get_python_version()
    python_version = re.sub(r'\s+', '-', python_version.lower())
    env_dir = os.path.join(WRACKER_DIR, 'envs', python_version)
    return env_dir


def ensure_clean_env(env_dir):
    if not os.path.exists(os.path.join(env_dir, 'bin', 'python')):
        subprocess.check_call(['virtualenv', '-p', PYTHON, env_dir])

        # Make it hard to install extra packages in a 'clean' env
        subprocess.check_call([os.path.join(env_dir, 'bin', 'pip'),
                               'uninstall', 'pip', '-y'])


def read_frozen_file(project_dir):
    """Get a list of (package_name, version) from the frozen file."""
    packages = []
    with open(os.path.join(project_dir, FROZEN_FILE)) as frozen_file:
        for line in frozen_file:
            req = Requirement(line.strip())
            assert len(req.specs) == 1 and req.specs[0][0] == '=='
            packages.append((req.key, req.specs[0][1]))
    return packages


def handle_exec(args):
    project_dir = look_up_for_file_or_die(FROZEN_FILE)
    env_dir = get_env_dir()
    ensure_clean_env(env_dir)
    platform = get_platform_info()


    # Use `python` from the clean env.  This is critical to work with pyenv, see
    # bug #2, while also hiding system modules.
    bin_path_items = [os.path.join(env_dir, 'bin')]
    python_path_items = []

    for frozen_params in read_frozen_file(project_dir):
        req = Requirement('%s==%s' % frozen_params)

        python_dir = python_path_for(platform, req)
        assert os.path.exists(python_dir), \
            "'%s' is not installed (did you run 'wracker install'?)" % (
                req.key,
            )
        python_path_items.append(python_dir)

        bin_dir = entrypoints.bin_path_for(platform, req)
        assert os.path.exists(bin_dir)
        bin_path_items.append(bin_dir)

    prepend_path('PYTHONPATH', python_path_items, sep=':')
    prepend_path('PATH', bin_path_items, sep=os.pathsep)

    os.environ['WRACKER_PYTHON'] = os.path.join(env_dir, 'bin', 'python')

    try:
        target = which(args[0])
    except IndexError:
        die("Must provide a command to run.")
    os.execv(target, args)


def parse_args(args):
    global PYTHON
    parser = argparse.ArgumentParser(
        prog='wracker',
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-p', '--python', help='The Python version to stub.')
    parser.add_argument('command',
                        help='The command to execute',
                        nargs='?',
                        default='install')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {0}'.format(__version__))
    parser.add_argument('exec_args',
                        nargs=argparse.REMAINDER,
                        help='Extra args for exec command')
    args = parser.parse_args(args)
    if args.python:
        PYTHON = args.python
    return args


def get_requirements(project_dir):
    """Get a list of requirements from the given dir.

    Returns a sequence of required packages, and an OrderedDict of locked
    packages.  The key is the package key, and the value is a
    pkg_resources.Requirement instance.  The required packages are
    non-exhaustive, only what's been asked for in the input file
    (e.g. requirements.in).

    Values for both the sequence and OrderedDict are pkg_resources.Requirement
    objects.

    (A pkg key is like a 'canonicalized' package name, a
    string. Requirement(s).key will generate the key for a package named `s`.)
    """
    locks = collections.OrderedDict()
    try:
        frozen_file = open(os.path.join(project_dir, FROZEN_FILE))
    except IOError as err:
        if err.errno != 2:  # Don't worry if there's no frozen file
            raise
    else:
        with frozen_file as infile:
            for line in infile:
                req = Requirement(line.strip())
                locks[req.key] = req

    requirements = collections.OrderedDict()
    with open(os.path.join(project_dir, INPUT_FILE)) as infile:
        for line in pkg_resources.yield_lines(infile):
            req = Requirement(line.strip())
            assert not req.key in requirements,\
                "Duplicate requirement " + req.key
            requirements.setdefault(req.key, req)

    return requirements, locks


def get_platform_info():
    """Collect all the variables needed for requirement environment checks.

    These can look something like this::

        pathlib2; python_version == "2.7" or python_version == "3.3"

    These variables have been found by trial and error.
    """

    script = ';'.join([
        'import json',
        'import platform',
        'version = platform.python_version_tuple()',

        # NOTE: This block is all one string! No trailing commas!
        'data = dict('
        'python_version=".".join(version[:2]),'
        'python_full_version=".".join(version),'
        'python_implementation=platform.python_implementation().lower()'
        ')',

        'print(json.dumps(data))',
    ])

    python_info_proc = subprocess.Popen(
        [PYTHON, '-c', script],
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE
    )
    python_info_proc.wait()

    python_info_raw = python_info_proc.stdout.read().strip()
    if python_info_proc.returncode != 0:
        print("Attempt to inspect Python failed with this output:",
              file=sys.stderr)
        print(python_info_raw, file=sys.stderr)
        sys.exit(1)

    # TODO: handle json parse error
    python_info = json.loads(python_info_raw)

    python_info.update({
        'sys_platform': sys.platform,
    })
    return python_info
