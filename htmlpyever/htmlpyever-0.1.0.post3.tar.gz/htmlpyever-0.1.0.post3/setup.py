#!/usr/bin/env python
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as setuptools_build_ext
from Cython.Build.Cythonize import cythonize
import lxml
import os

os.chdir(os.path.abspath(os.path.dirname(__file__)))

MODE = 'release'

class build_ext(setuptools_build_ext):
    def build_extension(self, ext):
        subprocess.check_call(['cargo', 'build'] + 
                              (['--release'] if MODE == 'release' else []))
        setuptools_build_ext.build_extension(self, ext)

with open('README.rst') as readme:
    description = readme.read()

includes = ['/usr/include/libxml2', '.'] + lxml.get_include()
setup(
    name='htmlpyever',
    version='0.1.0-3',

    description='Python bindings to html5ever',
    long_description=description,
    url='https://github.com/tbodt/htmlpyever',

    author='Theodore Dubois',
    author_email='tblodt@icloud.com',
    license = 'LGPLv3',

    classifiers=[
        'Development Status :: 4 - Beta',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.5',
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML"
    ],
    keywords=['html', 'html5', 'parser', 'parsing', 'html5ever'],

    ext_modules=cythonize([
        Extension(
            name='htmlpyever',
            sources=['htmlpyever.pyx'],
            libraries=['html5ever_glue', 'xml2'],
            library_dirs=['target/{}'.format(MODE)],
            include_dirs=includes,
            depends=['target/{}/libhtml5ever_glue.a'.format(MODE)],
        ),
    ], include_path=includes),

    setup_requires=['cython', 'lxml', 'pytest', 'pytest-runner'],
    install_requires=['lxml'],
    cmdclass={'build_ext': build_ext},
)
