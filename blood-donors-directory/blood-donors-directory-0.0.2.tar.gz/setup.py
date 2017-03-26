import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="blood-donors-directory",
    version="0.0.2",
    author="Akhil Lawrence",
    author_email="akhilputhiry@gmail.com",
    description=("A web application to maintain blood donors database"),
    license="GNU GPLv3",
    keywords="blood donation",
    url="https://github.com/akhilputhiry/blood-donors-directory",
    packages=['bdd'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: 2.7",
        "License :: Freeware",
    ],
)
