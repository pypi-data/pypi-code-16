from setuptools import setup, find_packages

long_desc = "A Sphinx extension providing a domain for describing Thrift services."

requires = [
    'Sphinx >= 1.0',
    'six'
]

setup(
    name='thriftdomain',
    version='1.2.0',
    url='http://bitbucket.org/bio-plus/sphinx-thriftdomain',
    license='Apache',
    author='Tom Davis',
    author_email='tom@neumitra.com',
    description='Sphinx domain for Thrift',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=['thriftdomain'],
    include_package_data=True,
    install_requires=requires
)
