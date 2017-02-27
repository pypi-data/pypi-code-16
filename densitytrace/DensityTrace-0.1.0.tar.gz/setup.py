from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='DensityTrace',
    version="0.1.0",
    description="DensityTrace",
    long_description=long_description,
    url="https://github.com/yuhangwang/DensityTrace",
    author="Yuhang(Steven) Wang",
    license="MIT/X11",
    packages=find_packages(),
    install_requires=[
            "typing",
            "numpy",
        ],
    )
