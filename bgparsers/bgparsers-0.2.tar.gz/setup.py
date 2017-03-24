from bgparsers import __version__
from setuptools import setup, find_packages

setup(
    name='bgparsers',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        "tqdm",
        "bgconfig",
        "itab",
        "click",
        "numpy",
        "intervaltree"
    ],
    entry_points={
            'console_scripts': [
                'bgvariants = bgparsers.commands.bgvariants:cli',
            ]
        }
)