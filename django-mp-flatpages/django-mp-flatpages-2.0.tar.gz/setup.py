
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='django-mp-flatpages',
    version='2.0',
    description='',
    long_description=open('README.md').read(),
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url='https://github.com/pmaigutyak/mp-flatpages',
    download_url='https://github.com/pmaigutyak/mp-flatpages/archive/2.0.tar.gz',
    packages=['flatpages'],
    license='MIT',
    install_requires=[
        'django-modeltranslation==0.11'
    ]
)
