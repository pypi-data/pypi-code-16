#!/usr/bin/env python
from setuptools import setup, find_packages, Distribution
import codecs
import os.path

# Make sure versiontag exists before going any further
Distribution().fetch_build_eggs('versiontag>=1.2.0')

from versiontag import get_version, cache_git_tag  # NOQA


packages = find_packages(exclude=(
    'sandbox',
    'sandbox.*',
))

install_requires = [
    'Django>=1.9.6',
    'djangorestframework>=3.3.3',
    'kafka-python>=1.2.2',
    'msgpack-python>=0.4.7',
]


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()


cache_git_tag()

setup(
    name='django-logpipe',
    description="Move data around between Python services using Kafka and Django Rest Framework serializers.",
    version=get_version(pypi=True),
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    author='Craig Weber',
    author_email='crgwbr@gmail.com',
    url='https://gitlab.com/thelabnyc/django-logpipe',
    license='ISC',
    packages=packages,
    include_package_data=True,
    install_requires=install_requires,
)
