from setuptools import setup
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'retsly'))

try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='retsly',
    version='1.0.9',
    description="A Python wrapper for the Retsly API (https://rets.ly)",
    long_description=read_md('README.md'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='retsly python sdk',
    url='https://github.com/retsly/retsly-python-sdk',
    author='Retsly Software Inc.',
    author_email='support@rets.ly',
    license='MIT',
    packages=[
        'retsly'
    ],
    install_requires=[
        'requests',
        'jsonurl'
    ]
)