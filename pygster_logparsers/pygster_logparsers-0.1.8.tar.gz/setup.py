

__title__ = 'pygster_logparsers'
__version__ = '0.1.8'
__author__ = 'Serg Belyakov  <serg@itlbs.ru>'


from distutils.core import setup

setup(
  name = __title__,
  packages = [__title__, ],
  version = __version__,
  description = 'HAProxy parser for pygster',
  long_description = open('README.md').read(),
  author = 'Serg Belyakov',
  author_email = 'serg@itlbs.ru',
  url = 'https://github.com/serg-it/pygster-parsers',
  license=open('LICENSE').read(),
  install_requires=['pygster==1.0.1', 'raven==6.0.0'],
  package_dir={'pygster_logparsers': 'pygster_logparsers'},
  zip_safe=False,
)
