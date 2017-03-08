from distutils.core import setup

from setuptools import PackageFinder

from NucleusUtils import __version__ as version

LIB_NAME = 'NucleusUtils'
setup(
    name='NucleusUtils',
    version=version,
    packages=PackageFinder.find(),
    url='https://bitbucket.org/illemius/nucleusutils',
    license='MIT',
    author='Illemius/Alex Root Junior',
    author_email='jroot.junio@gmail.com',
    description='Collection of Nucleus utils',
    keywords=[
        'Illemius',
        'NucleusUtils',
        'Utilities'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    install_requires=['jinja2']
)
