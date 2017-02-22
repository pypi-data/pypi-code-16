from distutils.core import setup

setup(
    name = 'simpletransfers',
    version = '1.1.1',
    description = 'Simple file transfer library',
    author = 'Jesters Ghost',
    author_email = 'jestersghost@gmail.com',
    url = 'https://bitbucket.org/jestersghost/simpletransfers',
    requires = ['ctxlogger'],
    package_dir = {'simpletransfers': '.'},
    packages = [
        'simpletransfers',
        'simpletransfers.tests',
    ],
    package_data = {'simpletransfers.tests': ['one.txt', 'test.zip']},
)
