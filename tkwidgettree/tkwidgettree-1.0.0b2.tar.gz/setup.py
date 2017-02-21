# vim:ts=4:sw=4:
import os
from setuptools import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name='tkwidgettree',
	version='1.0.0b2',
	author='Staffan Thomen',
	author_email = 'duck@shangtai.net',
	description = ('Convenience class for building Tk widgets trees from a dict or a JSON file'),
	license = 'BSD',
	keywords = 'Tk tkinter widget builder',
	packages=[ 'tkwidgettree' ],
	url = 'https://github.com/sthomen/tkwidgettree',
	long_description=read('README'),
	classifiers = [
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3'
	]
);
