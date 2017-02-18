
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='django-model-search',
    version='1.0',
    description='Django simple search package',
    long_description=open('README.md').read(),
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url='https://github.com/pmaigutyak/mp-search',
    download_url='https://github.com/pmaigutyak/mp-search/archive/1.0.tar.gz',
    packages=['model_search'],
    license='MIT'
)
