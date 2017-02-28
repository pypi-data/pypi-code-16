# -*- coding: utf-8 -*-

from setuptools import setup

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name="spotify-downloader",
    packages=["app"],
    entry_points={
        "console_scripts": ['spotify-dl = app.app:main']
    },
    version='0.4',
    keywords=['spotify', 'youtube'],
    description="A CLI tool to download albums on Spotify via youtube-dl.",
    long_description=long_descr,
    author="Anthony Bloomer",
    author_email="ant0@protonmail.ch",
    url="https://github.com/AnthonyBloomer",
    install_requires=[
        'eyed3',
        'spotipy',
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
)
