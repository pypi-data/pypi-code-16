from distutils.core import setup
setup(
  name = 'fara_principals',
  packages = ['fara_principals'], 
  version = '0.0.6',
  description = 'A web scraper designed to collect Foreign Principal' +\
      ' information from fara.gov',
  author = 'Timothy Ebiuwhe',
  author_email = 'timothy_ebiuwhe@live.com',
  url = 'https://github.com/tandalf/fara_principals', 
  download_url = 'https://github.com/tandalf/fara_principals/archive/master.zip', 
  keywords = ['foreign principals', 'fara.gov', 'FARA', 'scraper', 
    'scrapy', 'python'],
  install_requires = ['scrapy', 'requests', 'coverage', 'mock']
)