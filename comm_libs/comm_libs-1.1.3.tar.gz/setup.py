try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='comm_libs',
    version='1.1.3',
    author='1024',
    author_email='',
    packages=['comm_libs'],
    license='LICENSE.txt',
    description='comm_libs',
    long_description=open('README.txt').read(),
    install_requires=[
]
)