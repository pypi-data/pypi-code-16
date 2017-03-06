from setuptools import setup, find_packages

setup(
  name="taplytics",
  version="0.0.3",
  description="Taplytics Python ALPHA",
  author="Taplytics",
  url="https://github.com/taplytics/taplytics-python/",
  author_email="vic@taplytics.com",
  packages=find_packages(),
  keywords=['abtesting', 'testing', 'ab', 'taplytics', 'optimization','multivariate'],
  install_requires=[
    'requests'
  ]
)