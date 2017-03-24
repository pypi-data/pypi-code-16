from pip.req import parse_requirements
from setuptools import setup

setup(
    name='consul-cleanup',
    version='0.0.1',
    scripts=['consul-cleanup'],
    url='https://github.com/discobean/consul-cleanup',
    description='Cleans up dead consul hosts and services',
    install_requires=[
        'appdirs==1.4.3',
        'packaging==16.8',
        'pyparsing==2.2.0',
        'python-consul==0.7.0',
        'requests==2.13.0',
        'six==1.10.0' ],
    keywords='ebs ebspin ebs-pin'
)

