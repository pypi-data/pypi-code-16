from os import path
from bgparsers import __version__
from setuptools import setup, find_packages

with open(path.join(path.dirname(path.abspath(__file__)), 'requirements.txt')) as f:
    required = f.read().splitlines()

setup(
    name='bgparsers',
    version=__version__,
    packages=find_packages(),
    install_requires=required,
    entry_points={
            'console_scripts': [
                'bgvariants = bgparsers.commands.bgvariants:cli',
            ]
        }
)