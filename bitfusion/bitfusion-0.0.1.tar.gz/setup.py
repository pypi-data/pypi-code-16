from setuptools import setup, find_packages

DEPS = [
  'python-dateutil >= 2.6.0',
  'pytz >= 2016.10',
  'requests >= 2.13.0',
]

setup(
  name='bitfusion',
  version='0.0.1',
  description='Python SDK for developing against the Bitfusion Platform',
  packages=find_packages(),
  author='Brian Schultz',
  author_email='brian@bitfusion.io',
  url='http://www.bitfusion.io',
  install_requires=DEPS,
)
