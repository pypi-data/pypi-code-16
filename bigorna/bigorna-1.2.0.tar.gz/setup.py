#!/usr/bin/env python

from setuptools import setup, find_packages
from bigorna import __VERSION__ as version


def get_requirements(filename):
    with open(filename) as f:
        requirements_list = []
        rows = f.readlines()
        for row in rows:
            row = row.strip()
            if (row.startswith('#') or row.startswith('git+ssh://') or
                    row.startswith('-r') or not row):
                continue
            else:
                requirements_list.append(row)
    return requirements_list


setup(
    name='bigorna',
    version=version,
    description="Bigorna is a simple job manager to submit tasks.",
    url='https://github.com/cliixtech/bigorna/',
    author='Danilo Queiroz',
    author_email='dq@cliix.io',
    license="GPLv3",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='bigorna job tracker scheduler sysadmin',
    packages=find_packages(exclude=['tests']),
    test_suite='nose.collector',
    tests_require=get_requirements('dev_requirements.txt'),
    install_requires=get_requirements('requirements.txt'),
    extras_require={'test': get_requirements('requirements.txt')},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bigorna = bigorna.cli:main'
        ],
    }
)
