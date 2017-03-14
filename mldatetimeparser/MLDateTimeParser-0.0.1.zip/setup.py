# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
 name='MLDateTimeParser',
 version='0.0.1',
 description='machine learning based datetime string parser. it parse the text\
 string and return datetime  string.',
 long_description='long_description',
 url='https://github.com/harishank/MLDateTime-Parser',
 author='Harishankar Chinnathambi',
 author_email='hari29shankar@gmail.com',
 packages=['MLDateTimeParser',],
 license='MIT',
 classifiers=[
 'Programming Language :: Python ::2.6',
 'Programming Language :: Python ::2.7',
 ],
 keywords='MLDateTimeParser',
 install_requires=['numpy','scikitlearn']
)