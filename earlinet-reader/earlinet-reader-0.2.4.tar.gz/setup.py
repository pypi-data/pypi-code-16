#!/usr/bin/env python

from setuptools import setup
import os
import re
import io

# Read the long description from the readme file
with open("readme.rst", "rb") as f:
    long_description = f.read().decode("utf-8")


# Read the version parameters from the __init__.py file. In this way
# we keep the version information in a single place.
def read(*names, **kwargs):
    with io.open(
            os.path.join(os.path.dirname(__file__), *names),
            encoding=kwargs.get("encoding", "utf8")
    ) as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Run setup
setup(name='earlinet-reader',
      packages=['earlinet_reader', 'earlinet_reader.scripts'],
      package_data={'': ['templates/*',]},
      version=find_version("earlinet_reader", "__init__.py"),
      description='Package to read processed lidar data in the EARLINET NetCDF formats.',
      long_description=long_description,
      url='https://bitbucket.org/iannis_b/earlinet-reader/',
      author='Ioannis Binietoglou',
      author_email='ioannis@inoe.ro',
      license='MIT',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Atmospheric Science',
      ],
      keywords='lidar aerosol EARLINET',
      install_requires=[
          "numpy",
          "matplotlib",
          "sphinx",
          "jinja2",
          "netCDF4",
      ],
      entry_points={
          'console_scripts': ['plotELPP = earlinet_reader.scripts.plot_elpp:main',
                              'plotoptical = earlinet_reader.scripts.plot_optical:main'],
      },
      )
