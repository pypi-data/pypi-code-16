import os
from setuptools import setup
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='serverless_runlocal',
    author='Daisuke Takahashi @dt4k',
    author_email='d.takahashi1811@gmail.com',
    url='https://github.com/dtak1114/serverless_runlocal',
    version='0.1.2',
    license='MIT',
    packages=['serverless_runlocal'],
    install_requires=[
        'flask',
        'flasgger',
    ],
    keywords='serverless aws lambda flask local',
    description='Serverless configuration parser to run your serverless function as Flask.',
    #  long_description=read('README.md'),
    classifier=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'License :: OSI Approved :: MIT License',
        'Framework :: Flask'
    ]
)
