from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='streams_optimization',
    version='1.0.0.dev3',
    description='A library for LHCb trigger/stripping streams optimization',
    long_description=long_description,
    url='https://gitlab.cern.ch/YSDA/streams-optimization/tree/master',
    author='Yandex School of Data Analysis',
    author_email='kazeevn@yandex-team.ru',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Topic :: System :: Clustering'
    ],
    packages=find_packages(),
    install_requires=['ddt==1.1.1',
                      'numpy>=1.12.0', 
                      'lasagne>=0.2.dev1', 
                      'theano>=0.9.0rc2']
)
    
    
