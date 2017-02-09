from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = "Rumba",
    version = "0.1",
    url = "https://gitlab.com/arcfire/rumba",
    keywords = "rina measurement testbed",
    author = "Sander Vrijders",
    author_email = "sander.vrijders@intec.ugent.be",
    license = "LGPL",
    description = "Rumba measurement framework for RINA",
    long_description = long_description,
    packages = ["rumba", "rumba.testbeds", "rumba.prototypes"],
    install_requires = ["paramiko", "wheel"]
)
