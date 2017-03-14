from pip.req import parse_requirements
from setuptools import setup

setup(
    name='route53-pin',
    version='0.0.3',
    scripts=['route53-pin'],
    url='https://github.com/discobean/route53-pin',
    description='Pin internal route53 DNS entry to EC2 instance',
    install_requires=[
        'appdirs==1.4.3',
        'boto3==1.4.4',
        'botocore==1.5.25',
        'docutils==0.13.1',
        'futures==3.0.5',
        'jmespath==0.9.2',
        'packaging==16.8',
        'pyparsing==2.2.0',
        'python-dateutil==2.6.0',
        'requests==2.13.0',
        's3transfer==0.1.10',
        'six==1.10.0'],
    keywords='route53 route53pin route53-pin'
)
