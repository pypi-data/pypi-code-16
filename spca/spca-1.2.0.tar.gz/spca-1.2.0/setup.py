from setuptools import setup ,find_packages
from codecs import open
from os import path

here=path.abspath(path.dirname(__file__))
log_description=""
with open(path.join(here,'README.rst'),encoding='utf-8') as f:
	log_description=f.read()
	
setup(
name='spca',
version='1.2.0',
description='A simple implemetation of Principle Component Analysis',
long_description="A simple but great implementation of Principle component analysis. This module accepts a SVM format data in a file and expected value of variance with output file location. Reduces dimension and writes data back to output location",
url='https://github.com/salman-kgp/easypca',
author="Salman Ahmad",
author_email="salmaniit.ahmed1@gmail.com",
license='MIT',
classifiers=[
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'Topic :: Software Development :: Build Tools',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 2.7',
],
install_requires=['numpy','sklearn'],
keywords='dimension reduction pca machine learning',

)