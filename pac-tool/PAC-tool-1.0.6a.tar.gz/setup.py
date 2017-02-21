from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
      name = "PAC-tool",
      version = "1.0.6a",
      author = "Akis, Christina, Paschalis",
      author_email = "pnatsidis@hotmail.com",
      description = "This is our little project for GWAS",
      url = "https://github.com/pnatsi/PACtool",
      keywords = "project python linux gwas bioinfo-grad",
      packages = ['pactool'],
      license = 'MIT',
      install_requires = [
          'matplotlib',
          'numpy',
          'scipy',
          'pyliftover',
          'requests',
      ],
      package_data = {'data':['data/gwas.controls.gen', 'data/gwas.cases.gen']},
      include_package_data = True,
      long_description = '',
      )
