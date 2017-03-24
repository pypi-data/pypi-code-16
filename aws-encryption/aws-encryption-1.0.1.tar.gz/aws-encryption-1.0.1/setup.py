import sys
from setuptools import setup


if (
    'install' in sys.argv or  # pip
    'bdist_wheel' in sys.argv or  # pip
    '--dist-dir' in sys.argv and 'bdist_egg' in sys.argv  # easy_install
):
    raise ImportError('Did you mean to install aws-encryption-sdk?')

setup(
    name='aws-encryption',
    version='1.0.1',
    maintainer='Adam Johnson',
    maintainer_email='me@adamj.eu',
    url='https://github.com/adamchainz/aws-encryption',
)
