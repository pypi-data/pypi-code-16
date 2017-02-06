from distutils.core import setup
import setuptools
setup(
  name = 'globe',
  packages = ['globe', 'globe/connect', 'globe/connect/voiceLib'], # this must be the same as the name above
  version = '1.0.4',
  description = 'Globe Api ',
  author = 'clark galgo',
  author_email = 'clark21@dev-engine.net',
  url = 'https://github.com/globelabs/globe-connect-python', # use the URL to the github repo
  download_url = 'https://github.com/globelabs/globe-connect-python/archive/master.zip', # I'll explain this in a second
  keywords = ['Globe', 'Globe Api', 'Globe Labs'], # arbitrary keywords
  classifiers = [],
  install_requires = ['pycurl', 'StringIO==7.5']
)
