#!/usr/bin/env python
from setuptools import setup, Extension, find_packages
from setuptools.command.sdist import sdist as _sdist


try:
    from Cython.Build import cythonize
    extensions = cythonize(['src/cPrometheus.pyx'])
except ImportError:
    extensions = [
        Extension(
            'cPrometheus',
            ['src/cPrometheus.c']
        ),
    ]


class sdist(_sdist):
    def run(self):
        from Cython.Build import cythonize
        cythonize(['src/cPrometheus.pyx'])
        _sdist.run(self)


setup(
    name='cPrometheus',
    version='0.1',
    description="A monkey patch for prometheus_client, using GCC atomics for extra speed on CPython",
    author='James Pickering',
    author_email='james_pic@hotmail.com',
    license='MIT',
    url='https://github.com/jamespic/cPrometheus',
    download_url='https://github.com/jamespic/cPrometheus/archive/0.1.tar.gz',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=extensions,
    cmdclass={'sdist': sdist},
    setup_requires=[
        'cython',
    ],
    install_requires=[
        'prometheus_client>=0.0.12'
    ],
    test_suite='tests',
    keywords=['monitoring'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: System :: Monitoring'
    ],
)
