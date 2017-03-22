#!/usr/bin/env python3

from setuptools import setup

setup(
    name="unsplashdownloader",
    version="1.0",
    description="Download all images from a user page or collection in unsplash",
    author="Loic Reyreaud",
    author_email="reyreaud.loic@gmail.com",
    url="https://github.com/reyreaud-l/unsplashdownloader",
    download_url="https://github.com/reyreaud-l/unsplashdownloader/archive/1.0.tar.gz",
    keywords=["unsplash", "downloader", "wallpaper"],
    install_requires=["tqdm", "bs4", "slimit"],
    packages=["unsplashdownloader"],
    entry_points = {
        "console_scripts": ["unsplashdownloader=unsplashdownloader.crawl:main"]
        }
)
