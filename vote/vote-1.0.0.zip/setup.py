import ez_setup
ez_setup.use_setuptools()

import platform
import sys
from setuptools import setup, find_packages

from vote.version import __version__


entry_points = {}
entry_points['console_scripts'] = ['vote=vote.main:main']

setup(	
	name			= 'vote',
	version			= __version__,
	description		= 'A command line utility to vote on online polls.',
	author			= 'Amol Umrale',
	author_email 		= 'babaiscool@gmail.com',
	url			= 'http://pypi.python.org/pypi/vote/',
	packages		= find_packages(),
	include_package_data	= True,
	scripts			= ['ez_setup.py'],
	install_requires	= ['redlib>=1.5.6', 'redcmd>=1.2.10', 'htmq>=1.0.0', 'greencache>=1.0.0', 'requests>=2.10.0'],
	entry_points		= entry_points,
	classifiers		= [
					'Development Status :: 4 - Beta',
					'Environment :: Console',
					'License :: OSI Approved :: MIT License',
					'Natural Language :: English',
					'Operating System :: Microsoft :: Windows',
					'Programming Language :: Python :: 3.4',
				]
)
