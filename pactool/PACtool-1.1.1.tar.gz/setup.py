from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
    
setup(
      name = "PACtool",
      version = "1.1.1",
      author = "Akis, Christina, Paschalis",
      author_email = "pnatsidis@hotmail.com",
      description = "This is our little project for GWAS",
      url = "https://github.com/pnatsi/PACtool",
      keywords = "project python linux gwas bioinfo-grad",
      packages = ['pactool', 'analysis'],
      license = 'MIT',
      install_requires = [
          'matplotlib',
          'numpy',
          'scipy',
          'pyliftover',
          'requests',
      ],
      long_description = '',
      )
