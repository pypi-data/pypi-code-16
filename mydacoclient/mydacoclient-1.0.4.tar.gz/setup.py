from distutils.core import setup
setup(
  name = 'mydacoclient',
  packages = ['mydacoclient'], # this must be the same as the name above
  install_requires=[
    'requests',
  ],
  version = '1.0.4',
  description = 'python client for mydaco',
  author = 'Benjamin Bach',
  author_email = 'benjamin.bach@mydaco.com',
  url = 'https://github.com/mydaco/python-client', # use the URL to the github repo
  download_url = 'https://github.com/mydaco/python-client/archive/master.zip', # I'll explain this in a second
  keywords = ['mydaco', 'client'], # arbitrary keywords
  classifiers = [],
)
