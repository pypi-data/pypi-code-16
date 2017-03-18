from distutils.core import setup

setup(
    name = 'PMIofKCM',
    packages = ['PMIofKCM'],
    version = '1.0',
    description = 'PMIofKCM for KCM',
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/UDICatNCHU/PMIofKCM',
    download_url = 'https://github.com/UDICatNCHU/PMIofKCM/archive/v1.0.tar.gz',
    keywords = ['kcm',],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
        'pyprind',
        'simplejson',
        'pymongo'
    ],
    zip_safe=True
)
