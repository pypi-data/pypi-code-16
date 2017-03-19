from setuptools import Extension
from setuptools import setup


setup(
    name='hellfire',
    description=(
        'PATHspider Effects List Resolver'
    ),
    url='https://pathspider.net/hellfire',
    version='0.1.0',
    author='Iain R. Learmonth',
    author_email='irl@fsfe.org',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    setup_requires=['setuptools_golang'],
    ext_modules=[
        Extension('hellfire', ['hellfire.go']),
    ],
    build_golang={'root': 'pathspider.net/hellfire'},
)
