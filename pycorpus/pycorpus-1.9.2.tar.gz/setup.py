# coding=utf-8
from setuptools import setup

setup(
    name='pycorpus',
    version='1.9.2',
    author='Josu Bermudez',
    author_email='josubg@gmail.com',
    packages=['pycorpus', ],
    package_data={'pycorpus': ['ppss']},
    url='https://bitbucket.org/josu/pycorpus/',
    license='Apache License, Version 2.0',
    description='Easy concurrent launch of series of filebased experiments.',
    long_description=open('LONG.rst').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=['configargparse'],
    keywords='Parallel Experiment multiconfig',
)
