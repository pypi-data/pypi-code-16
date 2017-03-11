#!/usr/bin/python3 -S
import os
import uuid
from setuptools import setup, Extension
from pip.req import parse_requirements
from pkgutil import walk_packages
from Cython.Build import cythonize
from distutils.command.build_ext import build_ext

pathname = os.path.dirname(os.path.realpath(__file__))


PKG = 'faststart'
PKG_NAME = 'cy-faststart'
PKG_VERSION = '0.1.1'


# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(pathname + "/requirements.txt",
                                  session=uuid.uuid1())

def find_packages(prefix=""):
    path = [prefix]
    yield prefix
    prefix = prefix + "."
    for _, name, ispkg in walk_packages(path, prefix):
        if ispkg:
            yield name


class _build_ext(build_ext):
    def run(self):
        build_ext.run(self)

    def build_extension(self, ext):
        build_ext.build_extension(self, ext)


extensions = cythonize([
    Extension('faststart.cy_faststart', [pathname + '/faststart/cy_faststart.pyx'])
])


setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    description='A faststart implementation written in Cython.',
    author='Jared Lunde',
    author_email='jared@tessellate.io',
    url='https://github.com/jaredlunde/cy-faststart',
    license="MIT",
    install_requires=[str(ir.req) for ir in install_reqs],
    packages=list(find_packages(PKG)),
    ext_modules=extensions,
    cmdclass=dict(build_ext=_build_ext)
)
