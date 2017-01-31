#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from setuptools import setup, find_packages
import io
import os
import os.path as osp

name = 'schedula'
mydir = osp.dirname(__file__)


# Version-trick to have version-info in a single place,
# taken from: http://stackoverflow.com/questions/2058802/how-can-i-get-the-
# version-defined-in-setup-py-setuptools-in-my-package
##
def read_project_version():
    fglobals = {}
    with io.open(osp.join(
            mydir, name, '_version.py'), encoding='UTF-8') as fd:
        exec(fd.read(), fglobals)  # To read __version__
    return fglobals['__version__']


def get_long_description(cleanup=True):
    # noinspection PyBroadException
    try:
        from sphinx.application import Sphinx
        from sphinx.util.osutil import abspath
        import tempfile
        import shutil
        from sphinxcontrib.writers.rst import RstTranslator
    except:
        return ''
    outdir = tempfile.mkdtemp(prefix='setup-', dir='.')
    exclude_patterns = os.listdir(mydir or '.')
    exclude_patterns.remove('pypi.rst')

    app = Sphinx(abspath(mydir), './doc/', outdir, outdir + '/.doctree', 'text',
                 confoverrides={
                     'exclude_patterns': exclude_patterns,
                     'master_doc': 'pypi',
                     'dispatchers_out_dir': abspath(outdir + '/_dispatchers')
                 }, status=None, warning=None)

    app.builder.translator_class = RstTranslator
    app.build(filenames=[osp.join(app.srcdir, 'pypi.rst')])
    res = open(outdir + '/pypi.txt').read()
    if cleanup:
        shutil.rmtree(outdir)
    return res


proj_ver = read_project_version()
url = 'https://github.com/vinci1it2000/%s' % name
download_url = '%s/tarball/v%s' % (url, proj_ver)

setup(
    name=name,
    version=proj_ver,
    packages=find_packages(exclude=[
        'test', 'test.*',
        'doc', 'doc.*',
        'appveyor', 'requirements'
    ]),
    url=url,
    download_url=download_url,
    license='EUPL 1.1+',
    author='Vincenzo Arcidiacono',
    author_email='vinci1it2000@gmail.com',
    description='Produce a plan that dispatches calls based on a graph of '
                'functions, satisfying data dependencies.',
    long_description=get_long_description(),
    keywords=[
        "python", "utility", "library", "data", "processing",
        "calculation", "dependencies", "resolution", "scientific",
        "engineering", "dispatch", "scheduling", "simulink", "graphviz",
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Development Status :: 3 - Alpha",
        'Natural Language :: English',
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: European Union Public Licence 1.1 "
        "(EUPL 1.1)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=[
        'networkx',
        'dill',
        'graphviz',
        'docopt',
        'regex',
        'openpyxl>=2.4.0',
        'flask',
        'pycel',
        'sphinx',
        'decorator',
        'requests'
    ],
    dependency_links=[
        'https://github.com/vinci1it2000/pycel/tarball/master#egg=pycel-0.0.1'
    ],
    test_suite='nose.collector',
    setup_requires=['nose>=1.0'],
)
