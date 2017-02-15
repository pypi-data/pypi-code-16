# -*- coding:utf-8 -*-

from setuptools import setup

requirements = []
with open('requirements.txt') as f:
    requirements = [line.rstrip('\n') for line in f.readlines()]

readme = ''
with open('README.md') as f:
    readme = f.read()

setup(
    name='ez_spotify_dl',
    version='1.0',
    license='GPL',
    description='Spotify downloader tool',
    long_description=readme,
    url='https://bitbucket.org/sacanix/spotify_dl',
    author='Tony Kamillo',
    author_email='tonysacanix@gmail.com',
    keywords='spotify download tool',
    install_requires=requirements,
    py_modules=['spotify_dl'],
    include_package_data=True,
    # package_data={'': ['*.md', '*.txt']},
    entry_points={
        'console_scripts': ['spotify_dl = spotify_dl:main']
    }
)
