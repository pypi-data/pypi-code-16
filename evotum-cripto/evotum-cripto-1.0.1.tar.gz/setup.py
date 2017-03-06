# coding: latin-1

from setuptools import setup

setup(
    name = "evotum-cripto",
    version = "1.0.1",
    author = "André Baptista",
    author_email = "andre.baptista@devisefutures.com",
    description = ("eVotUM Cripto"),
    license = "GPL-3.0",
    keywords = "electronic vote crypto",
    url = "https://gitlab.com/eVotUM/Cripto-py",
    packages=["eVotUM", "eVotUM/Cripto"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    install_requires=[
        "colored==1.3.4",
        "jose==1.0.0",
        "python-cjson==1.2.1",
        "pyopenssl==16.2.0",
        "secretsharing==0.2.6",
        "pycryptodome==3.4.5"
    ],
)
