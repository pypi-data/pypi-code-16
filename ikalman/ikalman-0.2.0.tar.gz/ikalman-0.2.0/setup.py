# -*- coding: utf-8 -*-
from distutils.core import setup, Extension

setup(
        name="ikalman",
        ext_modules=[Extension("ikalman",
                               sources=["./python_bindings.c",
                                        "./gps.c",
                                        "./kalman.c",
                                        "./matrix.c"],
                               extra_compile_args=['-std=c99'])],
        version="0.2.0",
        author="Joshua Semar",
        author_email="joshua.semar@mapmyfitness.com",
        download_url='https://github.com/ruipgil/ikalman/archive/master.zip',
        url="https://github.com/ruipgil/ikalman",
        description = 'Python bindings for the ikalman c library'
      )

