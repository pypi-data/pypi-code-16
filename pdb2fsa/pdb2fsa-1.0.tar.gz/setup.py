from distutils.core import setup

setup(
  name = 'pdb2fsa',
  packages=['pdb2fsa'],# this must be the same as the name above
  version = '1.0',
#  scripts=['pdb2fsa/pyScript.py'],
  description = "there is a simple introduction",
  long_description="details",
  author = 'author',
  author_email = 'author_email@gmail.com',
  url = 'http://github_package', # use the URL to the github repo
  download_url = 'http://github_can_download_package',
  keywords = [], # arbitrary keywords
  classifiers = [],
#  install_requires = ['numpy>=1.1', 'pandas>=0.18'], # dependencies needed
  license="Apache-2.0",
#    entry_points = {
#        'console_scripts': [
#            'runname = pdb2fsa.pyScript:main'
#        ]
#  },
# you should change the runname
)
