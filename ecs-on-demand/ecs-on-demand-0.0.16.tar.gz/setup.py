import os
from setuptools import setup, find_packages
import warnings

setup(
    name='ecs-on-demand',
    version='0.0.16',
    packages=find_packages(),
    include_package_data=True,
    # namespace_packages = ['ecs_on_demand'],
    author="Jason Bartz",
    author_email="jason@jasonbartz.com",
    url="https://github.com/jasonbartz/ecs-on-demand",
    # download_url = "https://github.com/jasonbartz/ecs-on-demand/tarball/v0.0.1",
    keywords = ['amazon', 'ecs', 'aws', 'container', 'docker'],
    classifiers = [],
    extras_require={
        'not-lambda': ['boto3>=1.4.4'],
    }
)