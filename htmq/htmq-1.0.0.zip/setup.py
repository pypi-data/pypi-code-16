import ez_setup
ez_setup.use_setuptools()

import platform
import sys
from setuptools import setup, find_packages

from htmq.version import __version__


setup(	
	name			= 'htmq',
	version			= __version__,
	description		= 'A fluent interface python library to query html.',
	author			= 'Amol Umrale',
	author_email 		= 'babaiscool@gmail.com',
	url			= 'http://pypi.python.org/pypi/htmq/',
	packages		= find_packages(),
	include_package_data	= True,
	scripts			= ['ez_setup.py'],
	install_requires	= ['redlib>=1.5.6'],
	classifiers		= [
					'Development Status :: 4 - Beta',
					'Environment :: Console',
					'License :: OSI Approved :: MIT License',
					'Natural Language :: English',
					'Operating System :: Microsoft :: Windows',
					'Programming Language :: Python :: 3.4',
				]
)
