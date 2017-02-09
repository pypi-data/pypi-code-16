from distutils.core import setup
setup(
  name = 'ncsv',
  packages = ['ncsv'], 
  scripts = ['scripts/ncsv','scripts/fast-ncsv'],
  version = '0.15.0',
  description = 'Curses based delimited file (CSV) browser and pretty printer',
  author = 'Ville Rantanen',
  author_email = 'ville.q.rantanen@gmail.com',
  url = 'https://bitbucket.org/MoonQ/ncsv',
  download_url = 'https://bitbucket.org/MoonQ/ncsv/get/tip.tar.gz', 
  keywords = ['csv', 'curses', 'markdown'], 
  classifiers = [],
  license = 'MIT',
)
