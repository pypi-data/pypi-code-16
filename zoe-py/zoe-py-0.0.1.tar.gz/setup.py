try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='zoe-py',
    version='0.0.1',
    packages=['zoe'],
    url='https://github.com/PiotrDabkowski/Zoe',
    license='MIT',
    author='Piotr Dabkowski',
    author_email='piodrus@gmail.com',
    description='Wait for it!',
)