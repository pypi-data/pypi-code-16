from __future__ import print_function
from setuptools import setup
import io
import os

import tmmpy

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt')

setup(
    name='tmmpy',
    version=tmmpy.__version__,
    url='https://git.kern.phys.au.dk/SunTune/tmmpy/',
    license='MIT',
    author='Emil Haldrup Eriksen',
    install_requires=['numpy', 'scipy'],
    author_email='emher@au.dk',
    description='Implementation of the tmm method along with different extensions, e.g. to deal with incoherence',
    long_description=long_description,
    packages=['tmmpy'],
    include_package_data=True,
    platforms='any'
)
