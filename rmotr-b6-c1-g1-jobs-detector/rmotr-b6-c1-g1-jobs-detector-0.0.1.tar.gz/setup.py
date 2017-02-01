import os
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ["tests/"]

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import sys, pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='rmotr-b6-c1-g1-jobs-detector',
    version='0.0.1',
    description="rmotr.com Group 1 Project | Jobs Detector",
    author='Vojtech Kotek, Tracy Homer',
    author_email='kotek.vojtech@gmail.com',
    license='CC BY-SA 4.0 License',
    packages=['rmotr-b6-c1-g1-jobs-detector'],
    maintainer='kotek.co',
    tests_require=[
        'pytest==2.9.1',
    ],
    install_requires=[
        'bs4==0.0.1',
        'click==6.6',
        'responses==0.5.1'
    ],
    zip_safe=False,
    cmdclass={'test': PyTest},
    url = "https://github.com/vkotek/pyp-w3-gw-jobs-detector/",
    download_url="https://github.com/vkotek/pyp-w3-gw-jobs-detector/tarball/0.1",
)
# Dont think that was right, gave requiremnt parse  error.
# maybe add a new line
