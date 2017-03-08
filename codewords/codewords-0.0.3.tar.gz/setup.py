#! /usr/bin/python

"""
codewords - Simple python library to generate "code phrases" based on
provided lists of words and delimiters.

This project uses bumpversion so prior to a release you should run:

  $ bumpversion (major|minor|patch)

depending on which version you are wanting to increment.  See
https://github.com/peritus/bumpversion for more information and options.

"""

from setuptools import setup, find_packages
from distutils.core import Command
import codewords


class PylintCommand(Command):
    description = 'Executes pylint on the package specified.'
    user_options = [('package=', 'p', "the package to be pylint'ed")]

    def initialize_options(self):
        self.package = None

    def finalize_options(self):
        pass

    def run(self):
        if not self.package:
            exit("pylint command requires package option to be specified")
        from pylint.lint import Run
        Run(['--output-format=parseable', self.package])


setup(
    name="codewords",
    version=codewords.get_version(),
    author="Louis Zirkel III",
    author_email="zzzirk@gmail.com",
    description='CodeWords python lbrary',
    url='https://github.com/zzzirk/codewords',
    license="bsd3",
    keywords="codewords codename codephrase code name phrase",
    test_suite="tests",

    cmdclass={'pylint': PylintCommand},
    # test_suite="nose.collector",

    entry_points={
        'console_scripts': [
            'codewords=codewords.__main__:main',
        ]
    },

    packages=find_packages(),

    install_requires=[
    ],

    setup_requires=[
    ],

    tests_require=[
        "mock==2.0.0",
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Security',
        'Topic :: System',
        'Topic :: Utilities',
    ],

)
