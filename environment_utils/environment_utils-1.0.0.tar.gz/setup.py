from setuptools import setup

VERSION = '1.0.0'

setup(
    name='environment_utils',
    packages=['environment_utils'],
    version=VERSION,
    description='Environment utils library',
    author='Martin Borba',
    author_email='borbamartin@gmail.com',
    url='https://github.com/borbamartin/environment-utils',
    download_url='https://github.com/borbamartin/environment-utils/tarball/{}'.format(VERSION),
    keywords=['environment', 'utils'],
    classifiers=[],
    install_requires=[
        'enum34 >= 1.1.6',
    ]
)
