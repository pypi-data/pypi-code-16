from os.path import join, dirname

from setuptools import setup, find_packages

import easy_languages

__autor__ = 'Larty'


setup(
    name='easy_languages',
    version=easy_languages.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    include_package_data=True
)