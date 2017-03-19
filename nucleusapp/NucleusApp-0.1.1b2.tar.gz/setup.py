from distutils.core import setup

from setuptools import PackageFinder

version = __import__('NucleusApp').__version__

setup(
    name='NucleusApp',
    version=version,
    packages=PackageFinder.find(exclude=['example']),
    url='https://bitbucket.org/illemius/nucleus',
    requires=['NucleusUtils', 'schedule'],
    license='MIT',
    author='Alex Root Junior',
    author_email='jroot.junior@gmail.com',
    description='Framework for realising module-based applications',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
