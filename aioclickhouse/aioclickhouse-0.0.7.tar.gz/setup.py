from aioclickhouse import __version__
from setuptools import setup


def get_version():
    return '.'.join(map(str, __version__))


setup(
    name='aioclickhouse',
    version=get_version(),
    packages=['aioclickhouse'],
    url='https://bitbucket.org/new_ios_team/py_clickhouse_aio',
    license='',
    author='Dmitry Sobolev',
    author_email='ds@napoleonit.ru',
    description='Asynchronous connector to ClickHouse DBMS',
    install_requires=[
        'aiohttp>=1.3,<1.4',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
    ]
)
