""" A setuptools based setup module.

    Adapted from:
    https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
from codecs import open
from os import path
import glob

here = path.abspath(path.dirname(__file__))
try:
    long_description = open('README.md').read()
except:
    long_description = ""

data_files = [('', ['settings.json', 'special_text.txt', 'latex_template.txt'])]
directories = glob.glob('tex/logo/')
for directory in directories:
    files = glob.glob(directory + '*')
    data_files.append((directory, files))

setup(
    name='Constantine',
    version='1.0.4',
    description='A poster generator that does something that should have been automated ages ago.',
    long_description=long_description,
    url='https://github.com/icydoge/Constantine',
    author='C Shi',
    author_email='icydoge@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Text Processing :: General',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='pdf generator',
    py_modules=['main', 'utils'],
    install_requires=['requests'],
    data_files=data_files,
    extras_require={},
    entry_points={
        'console_scripts': [
            'Constantine=main',
        ],
    },
)
