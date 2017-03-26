from distutils.core import setup

setup(
    name="org-du",
    version="2017.03.26",
    description="du-like output for lines of GNU/Emacs Org-mode files",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/du-org",
    download_url="https://github.com/novoid/du-org/zipball/master",
    keywords=["orgmode", "org-mode", "du", "xdu", "visualization"],
    install_requires=["importlib", "logging", "argparse", "time", "codecs"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        ],
    long_description="""\
org-du
-----------------------------
This Python 3 script parses parses a list of Org-mode files and
generates output similar to "du" (disk usage) but with lines of
Org-mode instead of kilobytes.

The purpose of this script is to use its output as the input for "xdu" in order
to get a graphical visualization:

: org-du.py my_org_file.org another_org_file.org | xdu

The script accepts an arbitrary number of files (see your shell for
possible length limitations).

Please read https://github.com/novoid/org-de/ for further information and descriptions.
"""
)
