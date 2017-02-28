from setuptools import setup
from setuptools import find_packages

try:
    from pypandoc import convert_file
    long_description = convert_file('README.md', 'rst')
except ImportError:
    long_description = open('README.md').read()


setup(
    name='talkzoho',
    version='3.0.2',
    description='Asynchronous wrapper for Zoho\'s numerous APIs',
    long_description=long_description,
    url='https://github.com/A2Z-Cloud/Talk-Zoho',
    packages=find_packages(exclude=('tests', 'tests.*')),
    author='James Stidard',
    author_email='james.stidard@a2zcloud.com',
    keywords=['talkzoho', 'Zoho', 'async', 'tornado'],
    install_requires=[
        'fuzzywuzzy',
        'python-Levenshtein',
        'inflect',
        'tornado'])
