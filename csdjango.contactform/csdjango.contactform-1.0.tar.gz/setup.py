from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='csdjango.contactform',
      version=version,
      description="i18n ready contact form",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['csdjango'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'akismet',
          'Django>=1.10',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
