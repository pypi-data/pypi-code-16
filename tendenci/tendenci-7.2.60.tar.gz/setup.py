import os
import sys
import subprocess

from fnmatch import fnmatchcase
from distutils.util import convert_path
from setuptools import setup, find_packages

from tendenci import __version__ as version


def read(*path):
    return open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                *path)).read()

# Provided as an attribute, so you can append to these instead
# of replicating them:
standard_exclude = ["*.pyc", "*~", "*.bak", ".DS_Store"]
standard_exclude_directories = [
    ".*", "CVS", "_darcs", "./build",
    "./dist", "EGG-INFO", "*.egg-info"
]


# Copied from paste/util/finddata.py
def find_package_data(where=".", package="", exclude=standard_exclude,
        exclude_directories=standard_exclude_directories,
        only_in_packages=True, show_ignored=False):
    """
    Return a dictionary suitable for use in ``package_data``
    in a distutils ``setup.py`` file.

    The dictionary looks like::

        {"package": [files]}

    Where ``files`` is a list of all the files in that package that
    don't match anything in ``exclude``.

    If ``only_in_packages`` is true, then top-level directories that
    are not packages won't be included (but directories under packages
    will).

    Directories matching any pattern in ``exclude_directories`` will
    be ignored; by default directories with leading ``.``, ``CVS``,
    and ``_darcs`` will be ignored.

    If ``show_ignored`` is true, then all the files that aren't
    included in package data are shown on stderr (for debugging
    purposes).

    Note patterns use wildcards, or can be exact paths (including
    leading ``./``), and all searching is case-insensitive.
    """

    out = {}
    stack = [(convert_path(where), "", package, only_in_packages)]
    while stack:
        where, prefix, package, only_in_packages = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "Directory %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                if (os.path.isfile(os.path.join(fn, "__init__.py"))
                    and not prefix):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + "." + name
                    stack.append((fn, "", new_package, False))
                else:
                    stack.append((fn, prefix + name + "/", package,
                                    only_in_packages))
            elif package or not only_in_packages:
                # is a file
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        if show_ignored:
                            print >> sys.stderr, (
                                "File %s ignored by pattern %s"
                                % (fn, pattern))
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix + name)
    return out

def _is_requirement(line):
    """Returns whether the line is a valid package requirement."""
    line = line.strip()
    return line and not line.startswith("#")

def _read_requirements():
    """Parses the file requirements.txt for pip installation requirements.
    Returns the list of package requirements.
    """
    with open("requirements.txt") as requirements_file:
        contents = requirements_file.read()
        requirements = [line.strip() for line in contents.splitlines()
                        if _is_requirement(line)]
    return [req for req in requirements]

excluded_directories = standard_exclude_directories + ["example", "tests"]
package_data = find_package_data(exclude_directories=excluded_directories, only_in_packages=False)

DESCRIPTION = "Tendenci - The Open Source Membership Management Software"

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = subprocess.check_output(['pandoc', '-f', 'markdown', '-t', 'rst', 'README.md'])
except:
    LONG_DESCRIPTION = open('README.md').read()

setup(
    name='tendenci',
    version=version,
    packages=find_packages(),
    package_data=package_data,
    include_package_data=True,
    author='Tendenci',
    author_email='programmers@tendenci.com',
    url='http://github.com/tendenci/tendenci/',
    license='GPL3',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    install_requires=_read_requirements(),
)
