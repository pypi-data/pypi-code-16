from setuptools import setup

VERSION = '1.0.0'

setup(
    name='datetime_utils',
    packages=['datetime_utils'],
    version=VERSION,
    description='A DateTime Utils library',
    author='Martin Borba',
    author_email='borbamartin@gmail.com',
    url='https://github.com/borbamartin/datetime-utils',
    download_url='https://github.com/borbamartin/datetime-utils/tarball/{}'.format(VERSION),
    keywords=['datetime', 'utils'],
    classifiers=[],
    install_requires=[
        'enum34 >= 1.1.6',
        'python-dateutil >= 2.5.3',
        'pytz >= 2016.10',
    ]
)
