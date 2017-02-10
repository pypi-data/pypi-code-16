# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

class _Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

_NAME = "markdownmail"

setup(
        name=_NAME,
        description="E-mail with text and html content provided with markdown",
        long_description=open("README").read(),
        version='0.4.0',
        author="Yaal Team",
        author_email="contact@yaal.fr",
        keywords= "mail markdown yaal",
        url="http://hg." + _NAME + ".yaal.fr",
        packages=[
            _NAME,
            _NAME + "/styles",
        ],
        package_data={
            '': ['default.css'],
        },
        install_requires=[
            "Markdown==2.6.6",
            "Envelopes==0.4",
        ],
        classifiers=[
            "Programming Language :: Python",
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
        ],
        license="MIT",
        zip_safe = True,
        tests_require=['tox'],
        cmdclass= {'test': _Tox},
)

