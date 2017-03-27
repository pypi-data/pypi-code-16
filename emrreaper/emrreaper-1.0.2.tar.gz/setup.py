from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="emrreaper",
    version="1.0.2",
    description="Enforces emr sla with extreme prejudice!",
    long_description=long_description,
    author="Nicholas J",
    author_email="nicholas.a.johns5@gmail.com",
    license="MIT",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords="emr",
    packages=find_packages(),
    install_requires=[
        "appdirs==1.4.3",
        "boto3==1.4.4",
        "botocore==1.5.29",
        "click==6.7",
        "docutils==0.13.1",
        "jmespath==0.9.2",
        "packaging==16.8",
        "pyparsing==2.2.0",
        "python-dateutil==2.6.0",
        "s3transfer==0.1.10",
        "six==1.10.0"
    ],
    entry_points={
        'console_scripts': {
            'emrreaper = emrreaper.cli:run'
        }
    }
)
