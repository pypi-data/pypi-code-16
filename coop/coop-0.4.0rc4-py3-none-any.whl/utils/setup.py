import datetime
import os
import subprocess
from fnmatch import fnmatchcase
from itertools import filterfalse

from setuptools.command.sdist import sdist as base_sdist


class sdist(base_sdist):
    """Build assets using ``npm run clean; npm run build`` before packaging"""
    def run(self):
        self.compile_assets()
        base_sdist.run(self)

    def compile_assets(self):
        try:
            subprocess.check_call(['npm', 'run', 'clean'])
            subprocess.check_call(['npm', 'run', 'build'])
        except (OSError, subprocess.CalledProcessError) as e:
            print('Error compiling assets: ' + str(e))
            raise SystemExit(1)


def date_version():
    return datetime.datetime.utcnow().strftime('%Y.%m.%d.%H%M')


class PackageFinder(object):
    """
    A faster version of the PackageFinder from setuptools. It does not bother
    descending in to directories that have already been excluded, and excludes
    non-package directories (those without an __init__.py) as it goes. This
    automatically excludes ``node_modules/``, ``repos/``, and
    ``project/frontend/static/``, saving a bunch of directory walking.

    'where' is the root directory which will be searched for packages.

    'exclude' is a sequence of package names to exclude; '*' can be used
    as a wildcard in the names, such that 'foo.*' will exclude all
    subpackages of 'foo' (but not 'foo' itself).

    'include' is a sequence of package names to include.  If it's
    specified, only the named packages will be included.  If it's not
    specified, all found packages will be included.  'include' can contain
    shell style wildcard patterns just like 'exclude'.
    """
    def __init__(self, where, exclude, include):
        self.where = where
        self.includes = self._build_filter(*include)
        self.excludes = self._build_filter(
            'ez_setup', '*__pycache__', '*.*', *exclude)

    @classmethod
    def find(cls, where='.', exclude=(), include=('*',)):
        """
        Get a list of all packages in ``where``, that pass the ``include`` and
        ``exclude`` filters.
        """
        return sorted(list(cls(where, exclude, include)))

    def __iter__(self):
        """Return a list all Python packages found within directory 'where'"""
        return filter(self.includes, self._find_packages_iter(self.where))

    def _candidate_dirs(self, base_path):
        """Return all dirs in base_path that appear to be packages."""
        for root, dirs, files in os.walk(base_path, followlinks=True):
            # Exclude directories that contain a period, as they cannot be
            #  packages. Mutate the list to avoid traversal.
            dirs[:] = filterfalse(self.excludes, dirs)
            dirs[:] = (dir for dir in dirs
                       if self._looks_like_package(os.path.join(root, dir)))
            for dir in dirs:
                yield os.path.relpath(os.path.join(root, dir), base_path)

    def _find_packages_iter(self, base_path):
        """All the packages in ``base_path`` that are not otherwise excluded"""
        candidates = self._candidate_dirs(base_path)
        return (path.replace(os.path.sep, '.') for path in candidates)

    @staticmethod
    def _looks_like_package(path):
        """Does a directory look like a package?"""
        return os.path.isfile(os.path.join(path, '__init__.py'))

    @staticmethod
    def _build_filter(*patterns):
        """
        Given a list of patterns, return a callable that will be true only if
        the input matches at least one of the patterns.
        """
        return lambda name: any(fnmatchcase(name, pat=pat) for pat in patterns)


find_packages = PackageFinder.find
