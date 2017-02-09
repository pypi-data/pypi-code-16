import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='mezzanine-portfolio',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Django/Mezzanine portfolio application',
    long_description=README,
    url='https://github.com/izhukov1992/mezzanine-portfolio',
    author='Ilya Zhukov',
    author_email='izhukov1992@gmail.com',
)