import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Copied from https://github.com/celery/celery/blob/master/setup.py
# -*- Distribution Meta -*-
re_meta = re.compile(r'__(\w+?)__\s*=\s*(.*)')


def _add_default(m):
    attr_name, attr_value = m.groups()
    return ((attr_name, attr_value.strip("\"'")),)


def parse_dist_meta():
    """Extract metadata information from ``$dist/__init__.py``."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'markcaptcha', '__init__.py')) as meta_fh:
        distmeta = {}
        for line in meta_fh:
            if line.strip() == '# -eof meta-':
                break
            m = re_meta.match(line.strip())
            if m:
                distmeta.update(_add_default(m))
        return distmeta


meta = parse_dist_meta()
setup(
    name='MarkCaptcha',
    packages=['markcaptcha'],
    version=meta['version'],
    description='MarkCaptcha: 验证码样本标注工具',
    keywords=meta['keywords'],
    author=meta['author'],
    author_email=meta['contact'],
    url=meta['homepage'],
    license='MIT',
    platforms=['any'],
    install_requires=['PyQt5', 'requests'],
    classifiers=[
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': ['markcaptcha=markcaptcha.__main__:main']
    }
)
