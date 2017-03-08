#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools
import pypandoc

def main():

    setuptools.setup(
        name             = "tmux-control",
        version          = "2017.03.08.1536",
        description      = "configure and control tmux",
        long_description = long_description(),
        url              = "https://github.com/wdbm/tmux-control",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        install_requires = [
                           "propyte"
                           ],
        scripts          = [
                           "tmux-control.py"
                           ]
    )

def long_description(
    filename = "README.md"
    ):

    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
