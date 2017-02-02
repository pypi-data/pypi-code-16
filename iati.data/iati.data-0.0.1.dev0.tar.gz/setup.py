from setuptools import setup, find_packages

setup(
    name = 'iati.data',
    version = '0.0.1dev',
    description = 'A placeholder package for the upcoming iati.* software libraries',
    author = 'IATI Technical Team and other contributors',
    author_email = 'code@iatistandard.org',
    licence = 'MIT',
    packages = find_packages(exclude='tests')
)
