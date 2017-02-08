from setuptools import setup, find_packages
import os

version = '1.6.2'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.rst').read(),
])

setup(name='Solgema.RichMenu',
      version=version,
      description="Solgema RichMenu for Plone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Solgema',
      author='Martronic SA',
      author_email='martronic@martronic.ch',
      url='http://www.martronic.ch/plone_products/Solgema.RichMenu',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Solgema'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.linkintegrity',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
