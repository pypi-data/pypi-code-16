from setuptools import setup, find_packages
import os

version = '0.1'

long_description = ''
if os.path.exists("README.rst"):
    long_description = open("README.rst").read()

setup(name='adi.bookmark',
      version=version,
      description="Store bookmarks to a Plone-site or -folder.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
	"Framework :: Plone :: 3.2",
	"Framework :: Plone :: 3.3",
	"Framework :: Plone :: 4.0",
	"Framework :: Plone :: 4.1",
	"Framework :: Plone :: 4.2",
	"Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ida Ebkes',
      author_email='contact@ida-ebkes.eu',
      url='https://github.com/ida/adi.bookmark',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['adi'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
