from setuptools import setup
from codecs import open # To use a consistent encoding
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
	name='pysemigroup',
    version=open("VERSION").read().strip(),
    description="A python implementation of semigroup algorithms.",
    long_description=open('README.rst').read(),
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
      'Programming Language :: Python :: 2.7',
      'Topic :: Scientific/Engineering :: Mathematics',
    ],
    keywords='sagemath automata semigroups monoid regular language',
    author='Charles Paperman',
    author_email='charles.paperman@gmail.com',
    install_requires=[],
    url='http://github.com/charles-paperman/pysemigroup',
    license = "GPLv2+",
    packages=['pysemigroup'],
)
