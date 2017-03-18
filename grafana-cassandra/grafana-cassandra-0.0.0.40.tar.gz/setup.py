import os

from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='grafana-cassandra',
    version='0.0.0.40',
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
