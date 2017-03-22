import sys
import os

from setuptools import setup
from distutils.sysconfig import get_python_lib

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    long_description = readme.read()

setup(
    name = 'python-certifi-win32',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    description = 'Add windows certificate store to certifi cacerts.',
    long_description=long_description,
    author = 'Andrew Leech',
    author_email = 'andrew.leech@planetinnovation.com.au',
    license = 'BSD',
    url = 'https://gitlab.com/alelec/python-certifi-win32',
    packages = ['certifi_win32'],
    package_dir = {'certifi_win32': 'src'},
    data_files = [(get_python_lib(prefix=''), ['python-certifi-win32-init.pth'])],
    install_requires = ['wrapt>=1.10.4', 'wincertstore', 'certifi'],
)
