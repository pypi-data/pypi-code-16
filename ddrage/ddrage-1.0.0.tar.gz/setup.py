# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name = "ddrage",
    description = "Simulator for ddRADseq (double digest restriction site associdated DNA squencing) datasets. Generates reads (FASTQ format) that can be analyzed and validated using a ground truth file (YAML).",
    long_description = open("README.rst").read(),
    version = open("VERSION").read(),
    author = "Henning Timm",
    author_email = "henning.timm@uni-due.de",
    license = "MIT",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        ],
    install_requires = ["numpy", "numba", "matplotlib", "scipy", "pyyaml"],
    extras_require = {
        "BBD-visualization":  ["bokeh"],
        "documentaion": ["sphinx >= 1.5.0", "sphinx_rtd_theme"],
        },
    package_data={
        "ddrage": ["quality_profiles/*.qmodel", "barcode_handler/barcodes/*.txt"],
        },
    packages = find_packages(),
    entry_points={
        "console_scripts": [
            "rage = ddrage.__main__:main"
          ]
      },
    )
