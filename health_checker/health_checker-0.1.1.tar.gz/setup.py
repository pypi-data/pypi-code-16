from setuptools import setup, find_packages
from healthchecker import __version__


setup(
    name='health_checker',
    version=__version__,
    description='Check if several checks pass or not',
    url='https://bitbucket.org/sievetech/health-checker',
    packages=find_packages(exclude=['tests']),
)
