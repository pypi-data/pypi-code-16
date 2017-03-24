from distutils.core import setup
from setuptools import find_packages

setup(
	name='QuotaEngine', 
	author='Artem Dubrovskiy',
	author_email='ad13box@gmail.com',
	version='1.1',
	packages=find_packages(),
	install_requires=['PyQt5', 'bs4'],
	keywords='quota editor dimensions unicom intelligence utility',
	description='A quota editor',
	long_description=open('README.txt').read(),
	classifiers=[
	    'Programming Language :: Python :: 3.4',
	],
)