from setuptools import setup, find_packages
import os

version = '0.0.6'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='pyramid_exclusive_request_methods',
      version=version,
      description="",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Framework :: Pyramid',
          ],
      keywords='pyramid request_method exclusive',
      author='Moriyoshi Koizumi',
      author_email='mozo@mozo.jp',
      url='https://github.com/moriyoshi/pyramid_exclusive_request_methods',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyramid >= 1.7',
          ],
      tests_require=[
          'webtest',
          ],
      extras_require={
          'doc': ['sphinx', 'repoze.sphinx.autointerface'],
          },
      entry_points="",
      test_suite='pyramid_exclusive_request_methods.tests'
      )
