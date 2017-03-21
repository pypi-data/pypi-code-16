from setuptools import find_packages

from pkg_resources import WorkingSet

import pkg_resources


def rebuild_package(package, dest_dir):
    """Open up the package and run setup.py on it with lib and include dirs reset."""

    pkg = find_packages(include=package)

    dist_pkg = pkg_resources.working_set.find(pkg_resources.Requirement.parse(package))
    has_setuptools = dist_pkg is not None

    """pkg_resources.resource_filename(dist_pkg, 'setup.py')
    tst_map = pkg_resources.get_entry_map(dist_pkg)
    print "has_setuptools: {}".format(has_setuptools)
    print "tst_map: {}".format(tst_map)
    """
    print "PKGS: {}".format(pkg)
