from setuptools import setup, find_packages

setup(name='helloAaron',
      version=0.01,
      description='Python package example',
      url='http://aarontuor.site',
      author='Aaron Tuor',
      author_email='aarontuor@gmail.com',
      license='MIT',
      packages=find_packages(), # or list of packages path from this directory
      zip_safe=False,
      install_requires=[],
      classifiers=['Programming Language :: Python'],
      keywords=['Package Distribution'])
