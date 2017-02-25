from distutils.core import setup

setup(
    name = 'slothTw',
    packages = ['slothTw'],
    version = '1.2',
    description = 'API for feedback of Course',
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/Stufinite/slothTw',
    download_url = 'https://github.com/Stufinite/slothTw/archive/v1.2.tar.gz',
    keywords = ['feedback', 'campass'],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
        'djangoApiDec',
        'simplejson'
    ],
    zip_safe=True
)
