from distutils.core import setup
from setuptools import find_packages
from check_tier import VERSION


setup(
name='check-tier',
description='Django app to check tier before deployment.',
author='Level Up',
author_email='os@lvlup.us',
version=VERSION,
packages=find_packages(),
license='GPL v3',
long_description=open('README.txt').read(),
include_package_data=True,
)
