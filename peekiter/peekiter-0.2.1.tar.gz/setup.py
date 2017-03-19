# From http://peterdowns.com/posts/first-time-with-pypi.html
from peekiter import __VERSION, __AUTHOR
from distutils.core import setup
setup(
  name = 'peekiter',
  packages = ['peekiter'], # this must be the same as the name above
  version = __VERSION,
  description = 'PeekIter is a Python3 package that implements peeking into iterators via a wrapper class. Peeking means looking at the next element from a generator without consuming it.',
  author = __AUTHOR,
  author_email = 'rift95@live.se',
  url = 'https://github.com/Olian04/PyPeekIter', # use the URL to the github repo
  download_url = 'https://github.com/Olian04/PyPeekIter/tarball/0.1', # Still need to understand what this does....
  keywords = ['iter', 'iterator', 'generator', 'peek', 'loop'], # arbitrary keywords
  classifiers = [],
)
