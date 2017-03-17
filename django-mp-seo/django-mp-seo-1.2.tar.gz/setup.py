
from setuptools import setup, find_packages

from seo import __version__


setup(
    name='django-mp-seo',
    version=__version__,
    description='Django seo app',
    long_description=open('README.md').read(),
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url='https://github.com/pmaigutyak/mp-seo',
    download_url='https://github.com/pmaigutyak/mp-seo/archive/%s.tar.gz' % __version__,
    packages=find_packages(),
    license='MIT',
    install_requires=[
        'django-modeltranslation==0.11'
    ]
)
