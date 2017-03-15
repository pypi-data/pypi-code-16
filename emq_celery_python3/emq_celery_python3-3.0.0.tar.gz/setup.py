#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup

__author__ = 'bac'

setup(
    name='emq_celery_python3',
    version='3.0.0',
    keywords=('emq', 'celery'),
    description=u'用于使用EMQ来做为Celery的Broker',
    license='MIT License',
    install_requires=['galaxy_sdk_python3>=0.5', 'celery'],

    url="http://xiangyang.li/project/emq_celery",

    author='Shawn Li',
    author_email='shawn@xiangyang.li',

    packages=['emq_celery'],
    platforms='any',
)
