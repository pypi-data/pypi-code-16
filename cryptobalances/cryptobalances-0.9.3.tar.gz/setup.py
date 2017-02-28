from setuptools import setup, find_packages
from os.path import join, dirname


setup(
    name='cryptobalances',
    version='0.9.3',
    author='Aliaksandr Leonau',
    author_email='leonov.aleksandr.1987@gmail.com',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    description='Python module for getting the balance of a various crypto currency',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    url='https://github.com/AleksandrLeonov/Crypto-Balances',
    platforms='Linux',
    entry_points={
        'console_scripts': ['cryptobalances=cryptobalances.main:main'],
    },
    install_requires=['base58==0.2.4', 'steem==0.4.3'],
    test_suite='tests'
)
