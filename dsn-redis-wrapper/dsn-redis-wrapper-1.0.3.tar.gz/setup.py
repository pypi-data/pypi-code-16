# coding=utf-8
from setuptools import setup, find_packages

version = '1.0.3'

setup(
    name="dsn-redis-wrapper",
    version=version,
    packages=find_packages(exclude=['test']),
    install_requires=[
        'setuptools',
        'redis>=2.10.5',
        'hiredis>=0.2.0',
    ],
    zip_safe=False,
    author=['desean'],
    author_email=['desean66@outlook.com'],
    license='MIT',
    url='https://github.com/desean/redis-wrapper',
    description='A simple and lightweight wrapper for redis',
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
