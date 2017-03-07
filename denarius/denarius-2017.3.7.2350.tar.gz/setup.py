#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import setuptools

def main():

    setuptools.setup(
        name             = "denarius",
        version          = "2017.03.07.2350",
        description      = "currency and other utilities",
        long_description = long_description(),
        url              = "https://github.com/wdbm/denarius",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        py_modules       = [
                           "denarius"
                           ],
        install_requires = [
                           "currencyconverter",
                           "dataset",
                           "datavision",
                           "pyprel",
                           "propyte",
                           "denarius"
                           ],
        scripts          = [
                           "denarius_graph_Bitcoin.py"
                           ],
        entry_points     = """
            [console_scripts]
            denarius = denarius:denarius
        """
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
