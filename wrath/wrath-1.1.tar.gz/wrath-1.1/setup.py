from distutils.core import setup

setup(
    name = 'wrath',
    packages = ['wrath'],
    version = '1.1',
    description = 'A search Engine that use KCM & KEM api invented by UDIC at NCHU.',
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/Stufinite/wrath',
    download_url = 'https://github.com/Stufinite/wrath/archive/v1.1.tar.gz',
    keywords = ['Search Engine', 'campass'],
    classifiers = [],
    license='MIT',
    install_requires=[
        'djangoApiDec==1.2',
        'jieba==0.38',
        'pymongo==3.4.0',
        'PyPrind==2.9.9',
        'requests==2.12.3',
        'simplejson==3.10.0',
    ],
    zip_safe=True
)
