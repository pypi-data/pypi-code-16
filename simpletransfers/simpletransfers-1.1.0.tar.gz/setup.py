from __future__ import print_function, unicode_literals
from distutils.core import setup

setup(
    name = 'simpletransfers',
    version = '1.1.0',
    description = 'Simple file transfer library',
    author = 'Jesters Ghost',
    author_email = 'jestersghost@gmail.com',
    url = 'https://bitbucket.org/jestersghost/simpletransfers',
    install_requires = ['ctxlogger'],
    requires = ['Flask', 'paramiko', 'requests', 'suds'],
    package_dir = {'simpletransfers': '.'},
    packages = [
        'simpletransfers',
        'simpletransfers.tests',
    ],
    package_data = {'simpletransfers.tests': ['one.txt', 'test.zip']},
)
