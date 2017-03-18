import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
requirements = parse_requirements("requirements.txt", session=False)
test_requirements = parse_requirements("requirements-test.txt", session=False)


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def run_tests(self):
        import shlex
        import pytest
        errcode = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errcode)


setup(
    name='gtxamqp',
    version='2.1.11',
    url='http://github.com/devsenexx/gtxamqp',
    license='MIT License',
    author='Oded Lazar',
    tests_require=[str(ir.req) for ir in test_requirements if ir.req],
    install_requires=[str(ir.req) for ir in requirements if ir.req],
    dependency_links=[str(ir.link) for ir in requirements if ir.link],
    cmdclass={'test': PyTest},
    author_email='odedlaz@gmail.com',
    description='AMQP Reconnecting Client for Twisted',
    packages=find_packages(),
    include_package_data=True,
    platforms='linux',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    extras_require={
        'testing': ['pytest'],
    }
)
