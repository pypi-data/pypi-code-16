from setuptools import setup
setup(
  name = 'pysole',
  packages = ['pysole'], # this must be the same as the name above
  version = '0.1.11',
  description = 'pysole is a wrapper for simulating c-sharp console applications on any operating system that supports python.',
  author = 'Tristan Arthur',
  author_email = 'RGSStudios@outlook.com',
  install_requires=['pygame',],
  url = 'https://github.com/TreeStain/pysole', # use the URL to the github repo
  download_url = 'https://github.com/TreeStain/pysole/tarball/0.1', # I'll explain this in a second
  keywords = ['c-sharp', 'color', 'colour', 'console', 'display', 'dynamic', 'linux', 'mac', 'pygame', 'pysole', 'pyterm', 'python3', 'style', 'terminal', 'text', 'window', 'windows', 'wrapper'], # arbitrary keywords
  classifiers = [],
)

# python setup.py sdist bdist_wheel
# python setup.py sdist bdist_wheel upload
