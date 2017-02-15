#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import versioneer
from os.path import realpath, dirname, relpath, join
from setuptools import setup

ROOT = dirname(realpath(__file__))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pyyaml>=3.11',
    'lts-workflows',
]

test_requirements = [
    'snakemake>=3.10',
]

package_data = []

def package_path(path, filters=()):
    if not os.path.exists(path):
        raise RuntimeError("packaging non-existent path: %s" % path)
    elif os.path.isfile(path):
        package_data.append(relpath(path, 'lts_workflows_sm_scrnaseq'))
    else:
        for path, dirs, files in os.walk(path):
            path = relpath(path, 'lts_workflows_sm_scrnaseq')
            for f in files:
                if not filters or f.endswith(filters):
                    package_data.append(join(path, f))

suffixes = ('.rule', '.settings', '.sm', '.yaml', 'Snakefile', '.csv')
package_path(join(ROOT, "lts_workflows_sm_scrnaseq"), suffixes)

setup(
    name='lts_workflows_sm_scrnaseq',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="single-cell RNA sequencing snakemake workflow",
    long_description=readme + '\n\n' + history,
    author="Per Unneberg",
    author_email='per.unneberg@scilifelab.se',
    url='',
    packages=[
        'lts_workflows_sm_scrnaseq',
        'lts_workflows_sm_scrnaseq.tests',
    ],
    package_dir={'lts_workflows_sm_scrnaseq':
                 'lts_workflows_sm_scrnaseq'},
    package_data={'lts_workflows_sm_scrnaseq': package_data},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='lts_workflows_sm_scrnaseq',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='lts_workflows_sm_scrnaseq/tests',
    tests_require=test_requirements,
)
