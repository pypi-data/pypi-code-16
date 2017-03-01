# -*- coding: utf-8 -*-
from setuptools import setup
from codecs import open

with open('README.rst', 'r', 'utf-8') as f:
        readme = f.read()

setup(name='genmenu',
      version='0.1.8',
      description='A meal menu planner',
      long_description=readme,
      url='https://github.com/peerster/genmenu',
      author='Pär Berge',
      author_email='paer.berge@gmail.com',
      license='MIT',
      packages=['genmenu'],
      zip_safe=False)
