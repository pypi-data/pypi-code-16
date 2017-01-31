from distutils.core import setup

setup(
    name = 's3archive',
    packages = ['s3archive'],
    version = '0.0.2',
    description = 'An easy to use python3 package to archive files on Amazon S3.',
    author = 'Daniele Maccioni',
    author_email = 'komradstudios@gmail.com',
    url = 'https://github.com/GendoIkari/s3archive',
    download_url = 'https://github.com/GendoIkari/s3archive/tarball/v0.0.2',
    keywords = ['amazon', 's3', 'archive'],
    classifiers = [],
    install_requires=['boto3'],
)
