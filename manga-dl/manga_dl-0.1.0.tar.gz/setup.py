"""
LICENSE:
Copyright 2016 Hermann Krumrey

This file is part of manga_dl.

    manga_dl is a program that allows downloading manga files from various
    sources

    manga_dl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    manga_dl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with manga_dl.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

# imports
import os
from manga_dl.metadata import version
from setuptools import setup, find_packages


def readme():
    """
    Reads the readme file.

    :return: the readme file as a string
    """
    # noinspection PyBroadException
    try:
        # noinspection PyPackageRequirements
        import pypandoc
        with open('README.md') as f:
            # Convert markdown file to rst
            markdown = f.read()
            rst = pypandoc.convert(markdown, 'rst', format='md')
            return rst
    except:
        # If pandoc is not installed, just return the raw markdown text
        with open('README.md') as f:
            return f.read()


def find_scripts():
    """
    Returns a list of scripts in the bin directory

    :return: the list of scripts
    """
    try:
        scripts = []
        for file_name in os.listdir("bin"):
            if not file_name == "__init__.py" and os.path.isfile(os.path.join("bin", file_name)):
                scripts.append(os.path.join("bin", file_name))
        return scripts
    except OSError:
        return []


def classifiers():
    """
    :return: The list of classifiers applicable to this project
    """
    return [
        "Environment :: Console",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Topic :: Communications :: File Sharing",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ]


def dependencies():
    """
    :return: A list of dependencies
    """
    return ["raven", "irc", "bs4", "requests"]

setup(name="manga_dl",
      version=version,
      description="A Manga Downloader",
      long_description=readme(),
      classifiers=classifiers(),
      url="https://gitlab.namibsun.net/namboy94/manga-downloader",
      download_url="https://gitlab.namibsun.net/namboy94/manga-downloader/repository/archive.zip?ref=master",
      author="Hermann Krumrey",
      author_email="hermann@krumreyh.com",
      license="GNU GPL3",
      packages=find_packages(),
      install_requires=dependencies(),
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=find_scripts(),
      zip_safe=False)
