import sys
import os

from setuptools import setup

with open('README.rst') as f:
    readme = f.read()


if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel upload")
    sys.exit()

setup(
    name='blindspin',
    version='2.0.1',
    long_description=readme,
    packages=['blindspin'],
    url='https://github.com/kennethreitz/blindspin',
    license='MIT',
    author='Kennethreitz',
    author_email='me@kennethreitz.org',
    description='Braille Spinner for Click',
    extras_require={
        'test': [
            'click',
            'pytest',
            'six',
        ]
    }
)

