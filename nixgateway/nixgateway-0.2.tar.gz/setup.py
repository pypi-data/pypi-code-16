from setuptools import setup

setup(
  name = 'nixgateway',
  packages = ['nixgateway'],
  version = '0.2',
  description = 'Python bindings to the Nix Gateway API (https://web-nix.cloud.nexxera.com/)',
  author = 'Paulo Scardine',
  author_email = 'paulos@xtend.com.br',
  url = 'https://github.com/scardine/py-nixgateway',
  download_url = 'https://github.com/scardine/py-nixgatway/archive/0.2.tar.gz',
  keywords = ['nexxera', 'nix gateway', 'payments', 'api'],
  classifiers = [],
  install_requires=[
    'python-jose',
    'requests',
  ],
)