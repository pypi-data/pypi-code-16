from setuptools import setup

import basecash

try:
    import pypandoc
    try:
        pypandoc.get_pandoc_version()
    except IOError:
        pypandoc.pandoc_download.download_pandoc()
    long_description = pypandoc.convert_file('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

setup(
    name='basecash',
    version=basecash.__version__,
    license='BSD',
    author='Ruud de Jong',
    description='Basic home expense and budgetting tool',
    long_description=long_description,
    packages=['basecash'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 1 - Planning',
    ],
)
