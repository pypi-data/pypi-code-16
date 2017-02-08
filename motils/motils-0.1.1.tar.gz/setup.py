# from distutils.core import setup
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

# # Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='motils',
    version='0.1.1',
    packages=[''],
    url='https://github.com/neuhofmo/motils',
    license='MIT',
    author='Moran Neuhof',
    author_email='neuhofmo@gmail.com',
    description='A package containing local utilities for simplifying every day coding and scripting',
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    keywords='Everyday scripting and development tools',
    py_modules=["motils"]
)

