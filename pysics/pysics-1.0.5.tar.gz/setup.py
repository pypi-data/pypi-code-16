# https://github.com/{username}/{module_name}/archive/{tag}.tar.gz



from distutils.core import setup
setup(
  name = 'pysics',
  packages = ['pysics'], # this must be the same as the name above
  version = '1.0.5',
  description = 'A game engine with tools for making enemy AI (WIP)',
  author = 'jonay2000',
  author_email = 'jonabent@gmail.com',
  url = 'https://github.com/jonay2000/pysics', # use the URL to the github repo
  download_url = 'https://github.com/jonay2000/pysics/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['physics', 'python', 'game engine'], # arbitrary keywords
  classifiers = [],
  install_requires=['pygame']
)
