import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

version = '0.2'

install_requires = []
description = "Renders recursive structures in a terminal friendly way."

setup(name='treeify',
      version=version,
      description=description,
      long_description=description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
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
