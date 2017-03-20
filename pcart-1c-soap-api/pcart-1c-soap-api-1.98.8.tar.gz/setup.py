from distutils.core import setup
from setuptools import find_packages

INSTALL_REQUIREMENTS = [
    'pcart-core>=1.98.4',
    'pcart-catalog>=1.98.3',
    'pcart-customers>=1.98.3',
    'pcart-cart>=1.98.3',
    'lxml>=3.7.3',
    'pytz>=2016.10',
    'pytils>=0.3',
]

setup(
    name='pcart-1c-soap-api',
    version='1.98.8',
    author='Oleh Korkh',
    author_email='oleh.korkh@the7bits.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    license='BSD License',
    description='A powerful e-commerce solution for Django CMS',
    long_description=open('README.txt').read(),
    platforms=['OS Independent'],
    url='http://the7bits.com/',
    install_requires=INSTALL_REQUIREMENTS,
)