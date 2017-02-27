import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='pytest-appengine',
    url='https://github.com/novopl/pytest-appengine',
    version=read('VERSION').strip(),
    author="Mateusz 'novo' Klos",
    author_email='novopl@gmail.com',
    license='MIT',
    description='AppEngine integration that works well with pytest-django',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        l.strip() for l in read('requirements.txt').split() if '==' in l
    ],
    entry_points={
        'pytest11': ['appengine = pytest_appengine.plugin']
    },
    classifiers=[
        "Framework :: Pytest",
        "Topic :: Software Development :: Testing",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
)
