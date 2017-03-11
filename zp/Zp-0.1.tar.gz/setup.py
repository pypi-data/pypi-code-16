from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='Zp',
    version='0.1',
    packages=find_packages(),
    author='Klyuev O. O.',
    author_email='tulenivnebe@mail.ru',
    description='Field Zp module',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url=' '
)