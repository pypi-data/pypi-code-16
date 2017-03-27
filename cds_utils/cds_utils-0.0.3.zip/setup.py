# coding=utf-8
from setuptools import setup, find_packages

setup(
    name="cds_utils",
    version='0.0.3',
    keywords=("图灵CDS", "工具类"),
    description="图灵CDS工具类",
    license="MIT License",
    author="hc",
    author_email="huangcheng_cc@sina.com",
    package_data={'': ['*.*']},
    packages=find_packages(),
    platforms="any"
)