#!/usr/bin/env python

from setuptools import setup, find_packages


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name="juju-vnfm",
    version='1.0.0b2',
    author="Open Baton Team",
    author_email="dev@openbaton.org",
    description="The Python version of a Juju Vnfm for Open Baton",
    license="Apache 2",
    keywords="python vnfm nfvo open baton openbaton sdk juju",
    url="http://openbaton.github.io/",
    packages=find_packages(),
    scripts=['bin/jujuvnfm'],
    install_requires=['jujuclient==0.53.3', 'python-vnfm-sdk==3.2.0b3'],
    long_description=readme(),
    include_package_data=True,
    # zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python :: 3.5',
        "Intended Audience :: Developers",
        'Topic :: Software Development :: Build Tools',
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)
