from distutils.core import setup
from setuptools import setup, Extension
setup(
  name = 'sequential_procedure',
  packages = ['sequential_procedure'], # this must be the same as the name above
  version = '1.0.b1',
  description = 'A library that contains classes having methods that will help in estimating the sample size required for a statistical experiment. ',
  author = 'P Jishnu Jaykumar',
  author_email = 'jishnu.jayakumar182@gmail.com',
  py_modules=['sequential_procedure'],
  #url = 'https://github.com/peterldowns/mypackage', # use the URL to the github repo
  url = 'https://testpypi.python.org/pypi/sequential_procedure',
  #download_url = 'https://github.com/peterldowns/mypackage/archive/0.1.tar.gz', # I'll explain this in a second
  #download_url = 'https://testpypi.python.org/packages/1f/df/f8d2052dce13a0ce3a291000934215fac1e0f60377efd24966a6f6b7e37b/sequential_procedure-1.0.1.tar.gz',
  #keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  install_requires = [
	"numpy",
	"pandas",
	"openpyxl"
],
  classifiers = ['Development Status :: 3 - Alpha','Intended Audience :: Science/Research','Natural Language :: English','Operating System :: OS Independent','Programming Language :: Python :: 2.7','Topic :: Scientific/Engineering :: Bio-Informatics','Topic :: Scientific/Engineering :: Information Analysis'],
)


