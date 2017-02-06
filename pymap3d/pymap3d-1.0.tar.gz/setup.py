#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])

setup(name='pymap3d',
      packages=['pymap3d'],
      version = '1.0',
      author = 'Michael Hirsch, Ph.D.',
      url = 'https://github.com/scienceopen/pymap3d',
      install_requires=['geopy'],
	  )

