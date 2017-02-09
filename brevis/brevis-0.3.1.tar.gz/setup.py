from setuptools import setup

setup(
    name='brevis',
    version='0.3.1',
    description='Python client for the Brevis URL shortener API',
    url='http://github.com/admiralobvious/brevis-python-client',
    author='Alexandre Ferland',
    author_email='aferlandqc@gmail.com',
    license='MIT',
    packages=['brevis'],
    zip_safe=False,
    install_requires=[
        'requests>=2.12'
    ],
    tests_require=[
        'nose>=1.3'
    ],
    test_suite='nose.collector',
    platforms='any',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
