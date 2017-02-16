#!/usr/bin/env python

from __future__ import absolute_import
import codecs
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with codecs.open('README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    author='Francois Voron',
    author_email='francois.voron@nereo.fr',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    description='CAS 1.0/2.0 client authentication backend for Django (inherited from django-cas)',
    keywords=['django', 'cas', 'cas2', 'cas3', 'client', 'sso', 'single sign-on', 'authentication', 'auth'],
    license='BSD',
    long_description=readme,
    name='nereo-django-cas-ng',
    packages=['django_cas_ng', 'django_cas_ng.management', 'django_cas_ng.management.commands', 'django_cas_ng.migrations'],
    package_data = {
        'django_cas_ng': ['locale/*/LC_MESSAGES/*',],
    },
    url='https://github.com/Nereo/django-cas-ng',
    #bugtrack_url='https://github.com/mingchen/django-cas-ng/issues',  # not support this key
    download_url ='https://github.com/Nereo/django-cas-ng/releases',
    version='4.0.2',
    install_requires=['nereo-python-cas>=1.0.0'],
    zip_safe=False,  # dot not package as egg or django will not found management commands
)

