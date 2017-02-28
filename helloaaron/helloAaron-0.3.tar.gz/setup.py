from setuptools import setup, find_packages

setup(name='helloAaron',
      version=0.03,
      description='Python package example',
      url='http://aarontuor.site',
      author='Aaron Tuor',
      author_email='aarontuor@gmail.com',
      license='MIT',
      scripts=['bin/helloWorld.py'],
      packages=find_packages(), # or list of packages path from this directory
      zip_safe=False,
      install_requires=[],
      classifiers=['Programming Language :: Python'],
      keywords=['Package Distribution'])
