#!/usr/bin/env python

from distutils.core import setup

from utils.utils import get_version


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name="juju-vnfm",
    description="The Python version of a Juju Vnfm for Open Baton",
    version=get_version(),
    author="Open Baton Team",
    author_email="dev@openbaton.org",
    license="Apache 2",
    keywords="python vnfm nfvo open baton openbaton sdk juju",
    url="http://openbaton.github.io/",
    packages=['jujuvnfm', 'utils'],
    scripts=['bin/jujuvnfm'],
    install_requires=['jujuclient==0.53.3', 'python-vnfm-sdk'],
    long_description=readme(),
    include_package_data=True,
    package_data={'jujuvnfm': ['etc/*.svg']},
    data_files=[('etc/icon.svg', ['etc/icon.svg']),
                ('README.rst', ['README.rst'])],
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
