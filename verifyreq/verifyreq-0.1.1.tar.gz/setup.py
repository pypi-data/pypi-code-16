"""Setup script for mtg_ssm."""

import setuptools


# Get version information without importing the package
__version__ = None
exec(open('verifyreq/version.py', 'rt').read())

SHORT_DESCRIPTION = 'Tool to verify requirement file installations.'
LONG_DESCRIPTION = open('README.rst', 'rt').read()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Build Tools',
]

setuptools.setup(
    name='verifyreq',
    version=__version__,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='George Leslie-Waksman',
    author_email='waksman@gmail.com',
    url='https://github.com/gwax/verifyreq',
    packages=setuptools.find_packages(),
    license='MIT',
    platforms=['any'],
    keywords='distutils setuptools egg pip requirements',
    classifiers=CLASSIFIERS,
    entry_points={
        'console_scripts': [
            'verifyreq = verifyreq.cli:main',
        ],
    },
)
