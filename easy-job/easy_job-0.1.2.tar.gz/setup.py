from distutils.core import setup
from setuptools.command.test import test as TestCommand
import setuptools
import inspect
import sys
import os

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split('\\n') if req != '']


install_reqs = get_install_requirements('requirements.txt')

setup(
    name='easy_job',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    version='0.1.2',
    description='A lightweight background task runner',
    author='Mahdi Zareie',
    install_requires=install_reqs,
    author_email='mahdi.elf@gmail.com',
    url='https://github.com/inb-co/easy-job',
    keywords=['worker', 'task runner', 'lightweight job runner'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
