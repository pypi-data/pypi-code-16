from setuptools import setup, find_packages
from bir_api import VERSION

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name = 'intgr-bir-api',
    version = VERSION.replace(' ', '-'),
    description = 'An API for BIR1 (Baza Internetowa REGON 1) allows requesting for polish company data providing KRS, REGON or VAT number. It requires private GUS API key.',
    long_description = readme(),
    author = 'Integree Bussines Solutions',
    author_email = 'dev@integree.eu',
    url = 'https://github.com/integree/intgr-bir-api',
    download_url = 'https://pypi.python.org/packages/source/i/intgr-bir-api/intgr-bir-api-%s.zip' % VERSION,
    keywords = 'api bir bir1 gus krs regon nip vat utils integree',
    packages = find_packages(),
    include_package_data = True,
    license = 'MIT License',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires = [
        'django-appconf',
    ],
    zip_safe = False)
