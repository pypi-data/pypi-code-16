import os
import sys
from os.path import join

from setuptools import find_packages, setup

try:
    import pypandoc
    long_description = pypandoc.convert_file('README.md', 'rst')
except (OSError, IOError, ImportError):
    long_description = open('README.md').read()


def setup_package():
    src_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
    pytest_runner = ['pytest-runner'] if needs_pytest else []

    setup_requires = [] + pytest_runner
    install_requires = ['numpy>=1.9', 'scipy>=0.17.1']
    tests_require = ['pytest>=3']

    metadata = dict(
        name='scipy-sugar',
        version='1.0.0',
        maintainer="Danilo Horta",
        maintainer_email="horta@ebi.ac.uk",
        license="MIT",
        description="Missing SciPy functionalities.",
        long_description=long_description,
        url='http://github.com/glimix/scipy-sugar',
        packages=find_packages(),
        zip_safe=True,
        install_requires=install_requires,
        tests_require=tests_require,
        setup_requires=setup_requires,
        include_package_data=True,
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ])

    try:
        setup(**metadata)
    finally:
        del sys.path[0]
        os.chdir(old_path)


if __name__ == '__main__':
    setup_package()
