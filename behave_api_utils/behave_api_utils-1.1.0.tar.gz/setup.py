from setuptools import setup

VERSION = '1.1.0'

setup(
    name='behave_api_utils',
    packages=['behave_api_utils'],
    version=VERSION,
    description='API Services utils library to use with Behave projects',
    author='Martin Borba',
    author_email='borbamartin@gmail.com',
    url='https://github.com/borbamartin/behave-api-utils',
    download_url='https://github.com/borbamartin/behave-api-utils/tarball/{}'.format(VERSION),
    keywords=['api', 'rest', 'services'],
    classifiers=[],
    install_requires=[
        'enum34 >= 1.1.6',
        'requests >= 2.10.0',
        'urllib3 >= 1.16',
        'behave_logger >= 1.0.0',
    ]
)
