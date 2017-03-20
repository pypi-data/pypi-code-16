# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="watson_speech_to_text_websockets",
    version="0.1.0",
    description="A subclass of the Watson Developer Cloud Speech to Text class that supports websockets",
    license="MIT",
    author="Joshua B. Smith",
    author_email='kognate@gmail.com',
    url='https://github.com/kognate/watson_speech_to_text_websockets',
    packages=find_packages(),
    install_requires=[ 'watson_developer_cloud','websockets'],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ]
)
