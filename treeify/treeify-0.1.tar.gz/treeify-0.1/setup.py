import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

version = '0.1'

install_requires = []
description = "Renders recursive structures in a terminal friendly way."

setup(name='treeify',
      version=version,
      description=description,
      long_description=description,
      classifiers=[],
      keywords='',
      author='John Carlyle',
      author_email='treeify@jcarlyle.email',
      url='https://github.com/stealthycoin/treeify',
      license='',
      packages=find_packages('treeify'),
      package_dir={'': 'treeify'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires)
