from distutils.core import setup
setup(
  name = 'dir_client',
  py_modules = ['dir_client'], # this must be the same as the name above
  scripts = ['dir_client.py'],
  version = '0.3',
  description = 'Client for theappbin services directory managing server',
  author = 'theappbin',
  author_email = 'yash@theappbin.com',
  url = 'https://github.com/1upon0/theappbin-dir-client', # use the URL to the github repo
  download_url = 'https://github.com/1upon0/theappbin-dir-client/archive/0.3.tar.gz', # I'll explain this in a second
  keywords = ['api-client', 'theappbin-dir'], # arbitrary keywords
  license = "Apache 2.0",
  classifiers = [],
)
