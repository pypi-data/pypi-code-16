from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
import subprocess
from setuptools.command.install import install

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README'), encoding='utf-8') as f:
    long_description = f.read()


class MyInstall(install):
    def run(self):
        print("------")
        install.run(self)


setup(
        name = 'cfirst',
        version='0.1.0',
        description='Tookit for c program beginner.',
        long_description=long_description,
        url='https://www.gitbook.com/book/qorzj/first-book-of-coding',
        author='qorzj',
        author_email='inull@qq.com',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='cfirst',
        packages = ['cfirst'],

        cmdclass={'install': MyInstall},
        entry_points={
            'console_scripts': [
                'cfirst = cfirst.cfirst:main',
                ],
            },
    )


