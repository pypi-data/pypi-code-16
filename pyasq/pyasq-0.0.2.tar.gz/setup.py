import io
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

import pyasq

here = os.path.abspath(os.path.dirname(__file__))


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.rst')


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        # TODO: Re-enable linting in tests
        # when https://github.com/PyCQA/pylint/issues/1113 is fixed
        # self.test_args = ['--pylint', '--pylint-error-types=FEW']
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    author=pyasq.__author__,
    author_email='mail@jonrshar.pe',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    cmdclass={'test': PyTest},
    description=pyasq.__doc__,
    install_requires=['requests'],
    license='License :: OSI Approved :: ISC License (ISCL)',
    long_description=long_description,
    name='pyasq',
    packages=['pyasq'],
    platforms='any',
    tests_require=[
        'pylint',
        'pytest',
        'pytest-pylint',
        'responses',
    ],
    url='http://github.com/textbook/pyasq/',
    version=pyasq.__version__,
)
