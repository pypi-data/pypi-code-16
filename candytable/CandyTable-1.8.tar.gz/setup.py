# -*- coding: utf-8 -*-
from distutils.core import setup
long_description = ''
try:
    import subprocess
    import pandoc

    process = subprocess.Popen(
        ['which pandoc'],
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    pandoc_path = process.communicate()[0]
    pandoc_path = pandoc_path.strip('\n')

    pandoc.core.PANDOC_PATH = '/home/david/htdocs/HomeWork/Python-曾學文/hw1-CandyCrush/venv/lib/python3.5/site-packages/pandoc'

    doc = pandoc.Document()
    doc.markdown = open('README.md').read()

    long_description = doc.rst

except:
    pass

setup(
    name = 'CandyTable',
    packages = ['CandyTable'],
    version = '1.8',
    long_description=long_description,
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/david30907d/HomeWork/tree/master/Python-%E6%9B%BE%E5%AD%B8%E6%96%87/hw1-CandyCrush',
    download_url = 'https://github.com/david30907d/HomeWork/archive/v1.8.tar.gz',
    keywords = ['CandyTable',],
    classifiers = [],
    license='GPL3.0',
    install_requires=[
    ],
    zip_safe=True
)
