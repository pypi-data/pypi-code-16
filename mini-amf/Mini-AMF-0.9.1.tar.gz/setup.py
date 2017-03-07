#!/usr/bin/env python

# Copyright (c) The PyAMF Project.
# See LICENSE.txt for details.

import os.path
from setuptools import Feature, setup
import sys

try:
    from Cython.Build import cythonize
    have_cython = True
except:
    have_cython = False


name = "Mini-AMF"
description = "AMF serialization and deserialization support for Python"
url = "https://github.com/zackw/mini-amf"
author = "Zack Weinberg, The PyAMF Project"
author_email = "zackw@panix.com"
license = "MIT License"

classifiers = """
Intended Audience :: Developers
Intended Audience :: Information Technology
License :: OSI Approved :: MIT License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: C
Programming Language :: Python
Programming Language :: Cython
Programming Language :: Python :: 2.7
Topic :: Internet :: WWW/HTTP :: WSGI :: Application
Topic :: Software Development :: Libraries :: Python Modules
Development Status :: 5 - Production/Stable
"""

keywords = """
amf amf0 amf3 actionscript air flash flashplayer bytearray recordset
decoder encoder sharedobject lso sol
"""


class AccelFeature(Feature):
    def __init__(self, have_cython):
        self.have_cython = have_cython
        self.extensions = []

        Feature.__init__(
            self,
            description="optional C accelerator modules (broken)",
            standard=False,
            available=have_cython,
            ext_modules=self.extensions
        )

    def include_in(self, dist):
        if not self.have_cython:
            sys.stderr.write(
                "ERROR: Cython is required to compile accelerator modules.\n")
            sys.exit(1)

        sys.stderr.write(
            "WARNING: Accelerator modules are broken.\n"
            "WARNING: You should only use --with-accel "
            "if you are trying to fix them.\n")

        self.extensions.extend(cythonize("miniamf/_accel/*.pyx"))
        Feature.include_in(self, dist)


def get_version():
    """
    Retrieve the version number from miniamf/_version.py.  It is
    necessary to do this by hand, because the package may not yet be
    importable (critical dependencies, like "six", may be missing).

    This duplicates the tuple-to-string logic in miniamf/versions.py,
    but without any dependence on "six".
    """
    from ast import literal_eval
    import re

    try:
        unicode
    except NameError:
        unicode = str

    try:
        int_types = (int, long)
    except NameError:
        int_types = (int,)

    with open(os.path.join(os.path.dirname(__file__),
                           "miniamf/_version.py"), "rt") as f:
        vdat = f.read()
    m = re.search(
        r"(?ms)^\s*version\s*=\s*Version\(\*(\([^)]+\))\)",
        vdat)
    if not m:
        raise RuntimeError("failed to extract version tuple")

    vtuple = literal_eval(m.group(1))
    if not vtuple:
        raise RuntimeError("version tuple appears to be empty")

    v = []
    first = True
    for x in vtuple:
        if not first and isinstance(x, int_types):
            v.append(u'.')
        if isinstance(x, unicode):
            v.append(x)
        elif isinstance(x, bytes):
            v.append(x.decode("utf-8"))
        else:
            v.append(unicode(x))
        first = False

    return u''.join(v)


# Note: this logic is duplicated in doc/conf.py.
# We only want the flair on the Github page.
def get_long_description():
    with open(os.path.join(os.path.dirname(__file__),
                           "README.rst"), "rt") as f:
        text = f.read()
        cut = text.find("\nAutomatic build statuses\n")
        if cut != -1:
            return text[:cut]


def setup_package():
    setup(
        name=name,
        version=get_version(),
        description=description,
        long_description=get_long_description(),
        url=url,
        author=author,
        author_email=author_email,
        keywords=keywords.split(),
        license=license,
        packages=[
            "miniamf", "miniamf._accel", "miniamf.adapters", "miniamf.util"
        ],
        install_requires=["six", "defusedxml"],
        features={"accel": AccelFeature(have_cython)},
        test_suite="tests",
        zip_safe=True,
        extras_require={
            "docs": [
                "sphinx >= 1.5",
            ]
        },
        classifiers=[
            l for l in (ll.strip() for ll in classifiers.splitlines()) if l
        ],
    )


if __name__ == "__main__":
    setup_package()
