from distutils.core import setup
from setuptools import find_packages, setup

setup(name='fbadSpace',
      version='0.1',
      description='facebookads wrapper',
      author='Alberto Egido',
      author_email='alberto.egido@hotmail.com',
      packages=find_packages(exclude=['contrib', 'dist', 'docs', 'tests'])
     )