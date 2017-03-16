from distutils.core import setup

setup(
  name = 'carpathview',
  packages=['carpathview'],# this must be the same as the name above
  version = '1.4',
#  scripts=['carpathview/pyScript.py'],
  description = "there is a simple introduction",
  long_description="details",
  author = 'author',
  author_email = 'author_email@gmail.com',
  url = 'http://github_package', # use the URL to the github repo
  download_url = 'http://github_can_download_package',
  keywords = [], # arbitrary keywords
  classifiers = [],
  install_requires = ['', ''], # dependencies needed
  license="Apache-2.0",
#    entry_points = {
#        'console_scripts': [
#            'runname = carpathview.pyScript:main'
#        ]
#  },
# you should change the runname
)
