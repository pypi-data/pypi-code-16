from setuptools import setup, find_packages


with open('README.rst') as f:
    README = f.read()


with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().splitlines()


with open('test_requirements.txt') as f:
    TESTS_REQUIRE = f.read().splitlines()


setup(
    name='cacheutils',
    version='0.1.1',
    description='A bunch of cache utils.',
    long_description=README,
    author='cacheutils developers',
    maintainer=u'Nicol\xe1s Ram\xedrez',
    maintainer_email='nramirez.uy@gmail.com',
    license='BSD',
    packages=find_packages(exclude=('test', 'test.*')),
    entry_points={},
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=INSTALL_REQUIRES,
    extras_require={
        'hbase': [
            'happybase'
        ],
        'aerospike': [
            'aerospike'
        ]
    },
    tests_require=TESTS_REQUIRE
)
