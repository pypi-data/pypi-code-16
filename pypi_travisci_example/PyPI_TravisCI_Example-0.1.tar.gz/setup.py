import setuptools
from distutils.core import setup

setup(
  name='PyPI_TravisCI_Example',
  packages=['PyPI_TravisCI_Example'],
  version='0.1',
  description='An example for how to build project onto PyPI & TravisCI',
  author='aweimeow(Wei-You Chen)',
  author_email='aweimemow.tw@gmail.com',
  url='https://github.com/aweimeow/PyPI_TravisCI_Example',
  download_url=('https://github.com/aweimeow/PyPI_TravisCI_Example/archive/master.zip'),
  keywords=['PyPI', 'TravisCI', 'example'],
  classifiers=[],
  setup_requires=['pytest-runner'],
  tests_require=['pytest'],
)
