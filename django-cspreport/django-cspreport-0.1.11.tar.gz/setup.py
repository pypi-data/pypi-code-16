from distutils.core import setup

from setuptools import find_packages

setup(
  name='django-cspreport',
  packages=find_packages(),
  version='0.1.11',
  description='Django app for handling reports from web browsers of violations of content security policy.',
  author='Anton Tuchak',
  author_email='anton.tuchak@gmail.com',
  url='https://github.com/atuchak/django-cspreport',
  # download_url='https://github.com/atuchak/django-cspreport/archive/0.1.0.tar.gz',
  keywords=['Content-Security-Policy', 'csp', 'Django'],
  classifiers=[],
)