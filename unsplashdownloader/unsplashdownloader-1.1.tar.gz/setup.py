#!/usr/bin/env python3

import sys

if not sys.version_info >= (3, 0):
    print("Requires python3")
    sys.exit(255)

from setuptools import setup

setup(
    name="unsplashdownloader",
    version="1.1",
    description="Download all images from a user page or collection in unsplash",
    author="Loic Reyreaud",
    author_email="reyreaud.loic@gmail.com",
    url="https://github.com/reyreaud-l/unsplashdownloader",
    download_url="https://github.com/reyreaud-l/unsplashdownloader/archive/1.1.tar.gz",
    keywords=["unsplash", "downloader", "wallpaper"],
    install_requires=["tqdm", "bs4", "slimit"],
    packages=["unsplashdownloader"],
    entry_points = {
        "console_scripts": ["unsplashdownloader=unsplashdownloader.crawl:main"]
        }
)
