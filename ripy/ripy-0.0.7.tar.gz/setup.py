from __future__ import print_function
from setuptools import setup
import io
import os

import ripy

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
    name='ripy',
    version=ripy.__version__,
    url='https://git.kern.phys.au.dk/SunTune/ripy/',
    license='MIT',
    author='Emil Haldrup Eriksen',
    install_requires=['numpy', 'scipy', 'selenium', 'pandas', 'html5lib', 'bs4'],
    author_email='emher@au.dk',
    description='Parsing of refractive index data, designed to be used with the tmmpy package.',
    long_description=long_description,
    packages=['ripy'],
    include_package_data=True,
    platforms='any'
)
