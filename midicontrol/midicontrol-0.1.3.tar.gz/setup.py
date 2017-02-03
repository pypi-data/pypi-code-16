from distutils.core import setup
setup(
  name = 'midicontrol',
  packages = ['midicontrol'], # this must be the same as the name above
  version = '0.1.3',
  description = '',
  author = 'Wolfgang Steiner',
  author_email = 'wolfgang.steiner@gmail.com',
  url = 'https://github.com/wolfgangsteiner/midicontrol', # use the URL to the github repo
  download_url = 'https://github.com/wolfgangsteiner/midicontrol/tarball/0.1.2', # I'll explain this in a second
  keywords = ['midi', 'control'], # arbitrary keywords
  classifiers = [],
  install_requires=['mido','python-rtmidi'],
)
