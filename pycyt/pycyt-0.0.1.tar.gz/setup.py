import os
from setuptools import setup, find_packages
from distutils.util import convert_path


# Directory of script
root_dir = os.path.dirname(__file__)


# Get package version without importing it
version_ns = dict()
with open(convert_path('pycyt/version.py')) as fobj:
	exec(fobj.read(), version_ns)
version = version_ns['__version__']


# Dynamic download URL based off current version - git tag should match
download_url = (
	'https://github.com/jlumpe/pycyt/archive/{}.tar.gz'
	.format(version)
)


# Read readme file for long description
with open(os.path.join(root_dir, 'README.md')) as fobj:
	readme_contents = fobj.read()


setup(
	name='pycyt',
	version=version,
	description='Python package for the analysis of flow cytometry data',
	long_description=readme_contents,
	url='https://github.com/jlumpe/pycyt',
	author='Jared Lumpe',
	author_email='mjlumpe@gmail.com',
	classifiers=[
		'Development Status :: 2 - Pre-Alpha',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Operating System :: OS Independent',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Topic :: Scientific/Engineering',
		'Topic :: Scientific/Engineering :: Bio-Informatics',
	],
	packages=find_packages(),
	install_requires=[
		'numpy>=1.11',
	],
)
