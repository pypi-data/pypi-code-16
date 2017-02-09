import io
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

import zh_segment

class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

with io.open('README.rst', encoding='UTF-8') as reader:
    readme = reader.read()

setup(
    name='zh_segment',
    version=zh_segment.__version__,
    description='English word segmentation.',
    long_description=readme,
    author='Z&H',
    author_email='wuhaifengdhu@163.com',
    url='https://github.com/wuhaifengdhu/zh_segment/tree/master/docs',
    py_modules=['zh_segment'],
    packages=['zh_segment_data'],
    package_data={'zh_segment_data': ['*.txt']},
    tests_require=['tox'],
    cmdclass={'test': Tox},
    license='Apache 2.0',
    install_requires=[],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
