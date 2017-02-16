from setuptools import setup
import os
import codecs

try:
    # Python 3
    from os import dirname
except ImportError:
    # Python 2
    from os.path import dirname

here = os.path.abspath(dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding='utf-8') as f:
    long_description = '\n' + f.read()


requires = [
    'click==6.7',
    'bucketstore==0.1.1'
]


setup(
    name="s3env",
    version="0.0.2",
    author="Cameron Maske",
    description="Manipulate a key/value JSON object file in an S3 bucket through the CLI",
    long_description=long_description,
    author_email="cameronmaske@gmail.com",
    url='https://github.com/cameronmaske/s3env',
    py_modules=['s3env'],
    license='MIT',
    install_requires=requires,
    entry_points='''
        [console_scripts]
        s3env=s3env:cli
    ''',
)
