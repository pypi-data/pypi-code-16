import os

from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='grafana-cassandra',
    version='0.0.0.28',
    packages=find_packages(),
    include_package_data=True,
    description=("Json responder to interface between cassandra and grafana"),
    long_description=read('README'),
    install_requires=[
        'Cassandra-driver',
        'pyYAML', 'cherrypy',
    ],
    entry_points='''
        [console_scripts]
        grafana-cassandra=grafana_cassandra.server:main
    ''',
)
