from os import path
from setuptools import setup, find_packages


VERSION = '0.0.2'

here = path.abspath(path.dirname(__file__))


with open(path.join(here, 'README.rst')) as file:
    long_description = file.read()

setup(name='reloadable',
      version=VERSION,
      packages=find_packages(exclude=['*test*']),
      long_description=long_description,
      url='https://bitbucket.org/sievetech/reloadable',
      author='Diogo Magalhães Martins',
      author_email='magalhaesmartins@icloud.com',
      keywords='reloadable recover loop cli sieve')

# pre-publish :: pandoc --from=markdown --to=rst --output=README.rst README.md
