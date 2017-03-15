from distutils.core import setup
setup(
  name = 'Sonoff-Tasmota_autoflash',
  packages = ['Sonoff-Tasmota_autoflash'], # this must be the same as the name above
  version = 'v0.1.1',
  description = 'little python script to flash sonoff devices with the Tasmota software',
  author = 'Yann Doersam',
  author_email = 'yann.doersam@gmail.com',
  url = 'https://github.com/yann25/Sonoff-Tasmota_autoflash', # use the URL to the github repo
  download_url = 'https://github.com/yann25/Sonoff-Tasmota_autoflash/archive/v0.1.1tar.gz', # I'll explain this in a second
  keywords = ['ESP8266', 'flashing', 'sonoff', 'itead'], # arbitrary keywords
  classifiers = [],
)
