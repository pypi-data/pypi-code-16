#!/usr/bin/env python
from setuptools import setup


setup(name='collectd-cuda',
      version='0.0.1',
      description='CollectD plugin for Nvidia CUDA statistics',
      author='Jon Skarpeteig',
      author_email='jon.skarpeteig@gmail.com',
      url='https://github.com/Yuav/collectd-cuda',
      package_dir={'collectd_cuda': 'collectd_cuda'},
      keywords='collectd-cuda',
      include_package_data=True,
      install_requires=[
          'collectd'
      ],
      )
