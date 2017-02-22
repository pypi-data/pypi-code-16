from distutils.core import setup
v = '0.6'
setup(
  name = 'webmc',
  packages = ['webmc'], # this must be the same as the name above
  version = v,
  description = 'ffmpeg client for webm convertions',
  author = 'Nahuel Alonso',
  author_email = 'blizzard.nna@gmail.com',
  url = 'https://github.com/nahwar/webmc', # use the URL to the github repo
  download_url = 'https://github.com/nahwar/webmc/tarball/'+v, # I'll explain this in a second
  keywords = ['testing', 'logging', 'example', 'webm', 'ffmpeg'], # arbitrary keywords
  classifiers = [],
  scripts = ['webmc/webmc'],
)
