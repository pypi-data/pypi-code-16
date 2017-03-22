# -*- coding: utf8 -*-
from setuptools import setup
from os import path

if __name__ == '__main__':
    toplevel_dir = path.split(path.abspath(__file__))[0]
    setup(
        name='aiida',
        url='http://aiida.net/',
        license='MIT License',
        author='The AiiDA team',
        author_email='developers@aiida.net',
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
        ],
        version='0.8.0rc1',
        install_requires=[
            'aiida-core>=0.8.0rc1'
        ],
        long_description=open(path.join(toplevel_dir, 'README.rst')).read(),
    )
