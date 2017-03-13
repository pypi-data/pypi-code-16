# -*- coding: utf-8 -*-
import sys
import re
import os

from os.path import join, dirname

from setuptools import setup


VERSION_RE = re.compile(r'__version__ = \'([\d\.]+)\'')

LONG_DESCRIPTION = """
Python Social Auth is an easy to setup social authentication/registration
mechanism with support for several frameworks and auth providers.

It implements a common interface to define new authentication
providers from third parties. And to bring support for more frameworks
and ORMs.
"""


def long_description():
    try:
        return open(join(dirname(__file__), 'README.md')).read()
    except IOError:
        return None


def read_version():
    with open('pixelpin_auth_core/__init__.py') as file:
        version_line = [line for line in file.readlines()
                        if line.startswith('__version__')][0]
        return VERSION_RE.match(version_line).groups()[0]


def read_requirements(filename):
    with open(filename, 'r') as file:
        return [line for line in file.readlines() if not line.startswith('-')]


def read_tests_requirements(filename):
    return read_requirements('pixelpin_auth_core/tests/{0}'.format(filename))


PY = os.environ.get("BUILD_VERSION") or sys.version_info[0]
requirements_base = read_requirements('requirements-base.txt')
requirements = requirements_base + \
    read_requirements('requirements-python%s.txt' % PY)
requirements_openidconnect = \
    read_requirements('requirements-openidconnect.txt')
requirements_saml = read_requirements('requirements-saml-python%s.txt' % PY)

tests_requirements_base = read_tests_requirements('requirements-base.txt')
tests_requirements = tests_requirements_base + \
    read_tests_requirements('requirements-python%s.txt' % PY)

requirements_all = requirements_openidconnect + requirements_saml

tests_requirements = tests_requirements + requirements_all

setup(
    name='pixelpin-auth-core',
    version=read_version(),
    author=['Matias Aguirre', 'Callum Brankin'],
    author_email="callum@pixelpin.co.uk",
    description='Python PixelPin authentication made simple.',
    license='BSD',
    keywords='openid, oauth, saml, social auth, pixelpin auth, openid connect',
    url='https://github.com/PixelPinPlugins/pixelpin-auth-core',
    packages=[
        'pixelpin_auth_core',
        'pixelpin_auth_core.backends',
        'pixelpin_auth_core.pipeline',
        'pixelpin_auth_core.tests',
        'pixelpin_auth_core.tests.actions',
        'pixelpin_auth_core.tests.backends',
        'pixelpin_auth_core.tests.backends.data'
    ],
    long_description=long_description() or LONG_DESCRIPTION,
    install_requires=requirements,
    extras_require={
        'openidconnect': [requirements_openidconnect],
        'saml': [requirements_saml],
        'all': [requirements_all]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Internet',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
    package_data={
        'pixelpin_auth_core/tests': [
            'pixelpin_auth_core/tests/*.txt',
            'pixelpin_auth_core/tests/testkey.pem'
        ]
    },
    include_package_data=True,
    tests_require=tests_requirements,
    test_suite='pixelpin_auth_core.tests',
    zip_safe=False
)
