from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
      name = "PACtool",
      version = "1.0.5c",
      author = "Akis, Christina, Paschalis",
      author_email = "pnatsidis@hotmail.com",
      description = "This is our little project for GWAS",
      url = "https://github.com/pnatsi/PACtool",
      keywords = "project python linux gwas bioinfo-grad",
      packages = ['pactool', 'data'],
      license = 'MIT',
      install_requires = [
          'matplotlib',
          'numpy',
          'scipy',
          'pyliftover',
          'requests',
      ],
      data_files = {'data':['data/gwas.controls.gen', 'data/gwas.cases.gen']},
      long_description = '',
      )
