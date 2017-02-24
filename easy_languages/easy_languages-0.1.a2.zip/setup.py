from os.path import join, dirname

from setuptools import setup, find_packages

import easy_languages



setup(
    name='easy_languages',
    version=easy_languages.__version__,
    packages=find_packages(),
	description=open(join(dirname(__file__), 'README.txt')).read(),
	long_description="*soon*",
	author="Larty",
    include_package_data=True
)