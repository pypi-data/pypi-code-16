# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='easyRedisCache',
    version='0.15',
    author=u'David Ziegler',
    author_email='webmaster@SpreadPost.de',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/InfinityMod/easyRedisCache',
    license='BSD',
    description='Easy lock secured cache for redis',
    zip_safe=False,
    keywords=['cache', 'lock', 'redis', 'easy'],
    dependency_links=[
        "git+ssh:git@github.com:InfinityMod/easyRedisCache.git#egg=redisSherlock-0.3.0"
    ],
    install_requires=[
        'redisSherlock',
        'redis'
    ],
)