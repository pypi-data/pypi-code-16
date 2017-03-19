# From http://peterdowns.com/posts/first-time-with-pypi.html

from distutils.core import setup
setup(
  name = 'peekiter',
  packages = ['peekiter'], # this must be the same as the name above
  version = '0.2',
  description = 'A Python3 package that implements peeking into iterators via a wrapper class.',
  author = 'Olian04',
  author_email = 'peterldowns@gmail.com',
  url = 'https://github.com/Olian04/PyPeekIter', # use the URL to the github repo
  download_url = 'https://github.com/Olian04/PyPeekIter/tarball/0.1', # I'll explain this in a second
  keywords = ['iter', 'iterator', 'generator', 'peek'], # arbitrary keywords
  classifiers = [],
)
