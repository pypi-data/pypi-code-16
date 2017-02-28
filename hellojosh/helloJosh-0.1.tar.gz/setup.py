from setuptools import setup, find_packages

setup(name='helloJosh',
      version=0.01,
      description='Python package example',
      url='http://mywebsite_foo',
      author='josh',
      author_email='osbornj7@wwu.edu',
      license='MIT',
      packages=find_packages(), # or list of packages path from this directory
      zip_safe=False,
      install_requires=[],
      classifiers=['Programming Language :: Python'],
      keywords=['Package Distribution'])
