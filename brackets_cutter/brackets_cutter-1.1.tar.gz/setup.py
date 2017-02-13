from setuptools import setup, find_packages
from os.path import join, dirname
import brackets_cutter

setup(
    name='brackets_cutter',
    version=brackets_cutter.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    test_suite='tests',
    entry_points={
        'console_scripts':
            ['brackets_cutter = brackets_cutter.core:main'],
    }
)
