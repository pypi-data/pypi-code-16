import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='cartridge-stats',
    version='0.1',
    packages=['cartridge-stats'],
    description='A simple Cartridge addon for sales reporting',
    long_description=README,
    author='Josh Batchelor',
    author_email='josh.batchelor@gmail.com',
    url='https://github.com/joshbatchelor/cartridge-stats/',
    license='MIT',
    install_requires=[
        'Django>=1.6,<1.7',
    ]
)
