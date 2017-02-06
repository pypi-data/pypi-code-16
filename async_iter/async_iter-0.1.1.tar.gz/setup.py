from distutils.core import setup
from async_iter.async_iter import __version__
setup(
  name = 'async_iter',
  packages = ['async_iter'], # this must be the same as the name above
  version = __version__,
  description = 'A tool can easily parallelize functions',
  author = 'weidwonder',
  author_email = 'weidwonder@gmail.com',
  url = 'https://github.com/weidwonder/async-iter', # use the URL to the github repo
  download_url = 'https://github.com/weidwonder/async-iter/archive/master.zip',
  keywords = ['async', 'thread', 'gevent', 'parallelize'], # arbitrary keywords
  classifiers = [
      "Development Status :: 3 - Alpha",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      'Topic :: Software Development :: Build Tools',
      "Operating System :: OS Independent",
      "Programming Language :: Python :: 2.7",
      "Programming Language :: Python :: 3.5",
  ],
)