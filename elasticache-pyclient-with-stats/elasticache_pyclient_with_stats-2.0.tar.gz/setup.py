from setuptools import setup, find_packages

PACKAGE = "elasticache_pyclient_with_stats"
NAME = "elasticache_pyclient_with_stats"
KEYWORDS = ("aws", "ealsticache")
VERSION = '2.0'
DESCRIPTION = "pythone client for elasticache auto discovery with getting stats function"
LICENSE = 'LGPL'
URL = "https://github.com/LyuGGang/elasticache_pyclient"
AUTHOR = "LyuGGang"
AUTHOR_EMAIL = "me@lyuwonkyung.com"

setup(
    name = NAME,
    version = VERSION,
    keywords = KEYWORDS,
    description = DESCRIPTION,
    license = LICENSE,

    url = URL,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,

    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = ['python-memcached', 'hash_ring', 'python-memcached-stats'],
    )
