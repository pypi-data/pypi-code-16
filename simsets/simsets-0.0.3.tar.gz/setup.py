from setuptools import setup

setup(name='simsets',
      version='0.0.3',
      description='Create simulated datasets from original datasets',
      url='http://github.com/staeiou/simsets',
      author='Stuart Geiger',
      author_email='stuart@stuartgeiger.com',
      license='MIT',
      packages=['simsets'],
      install_requires=[
          'numpy', 'pandas'],
      zip_safe=False)
