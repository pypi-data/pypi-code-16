# coding=utf8

__author__ = 'liming'

from setuptools import setup

setup(name='saltedpwd',
      version='0.0.1',
      description='Generate safe password with random salt',
      url='https://github.com/ipconfiger/saltedpwd',
      author='Alexander.Li',
      author_email='superpowerlee@gmail.com',
      license='GNU GENERAL PUBLIC LICENSE3.0',
      packages=['saltedpwd'],
      install_requires=[],
      entry_points = {
        'console_scripts': [
            'hash_pwd=saltedpwd.functions:hash_pwd',
            'verify_pwd=saltedpwd.functions:verify_pwd',
        ],
      },
      zip_safe=False)