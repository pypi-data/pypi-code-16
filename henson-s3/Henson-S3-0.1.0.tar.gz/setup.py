from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        super().finalize_options()
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


def read(filename):
    with open(filename) as f:
        return f.read()

setup(
    name='Henson-S3',
    version='0.1.0',
    author='Andy Dirnberger',
    author_email='andy@dirnberger.me',
    url='https://henson-s3.readthedocs.io',
    description='A library for easily using S3 in a Henson application.',
    long_description=read('README.rst'),
    license='MIT',
    py_modules=['henson_s3'],
    zip_safe=False,
    python_requires='>=3.5',  # async/await
    install_requires=[
        'boto3',
        'Henson',
    ],
    tests_require=[
        'pytest',
        'pytest-asyncio',
    ],
    cmdclass={
        'test': PyTest,
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
    ]
)
