#!/usr/bin/env python

from distutils.core import setup
import sys
# if sys.version_info.major >= 3:
#     print("This package currently supports only python 2.x (for now!).")
#     sys.exit(1)

setup(name='pyLCSIM',
      version='0.4.0',
      description='Simulate X-ray lightcurves',
      author='Riccardo Campana',
      author_email='campana@iasfbo.inaf.it',
      license='MIT',
      url='http://pabell.github.io/pylcsim/html/index.html',
      packages=['pyLCSIM', 'pyLCSIM.psd_models'],
      requires=['numpy (>=1.8)', 'astropy (>=0.3)']
     )
