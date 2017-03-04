#!/usr/bin/env   python
import os
import setuptools

setuptools.setup(

        scripts = ['bin/pymiaopai_cli'],
	name='pymiaopai',
	version = '2017.3.7',
	keywords = 'miaopai',
	description = 'A python library for downloading miao pai vidoe.',
	long_description=open(
		os.path.join(os.path.dirname(__file__),'README.rst')).read(),
		author = 'fanlt',
		author_email = 'litton.van@gmail.com',
		url = 'https://github.com/litton/MiaoPaiVideo',
		packages = setuptools.find_packages(),
		license = 'APACHE'
      		)
