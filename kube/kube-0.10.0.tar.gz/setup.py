"""Python setuptools build script."""

import setuptools


# The following line gets parsed by sphinx, be aware when modifying it.
__version__ = '0.10.0'


INSTALL_REQUIRES = [
    'requests',
    'http-parser',
    'pyrsistent',
]


CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
]


setuptools.setup(
    name='kube',
    version=__version__,
    author='Floris Bruynooghe',
    author_email='flub@cobe.io',
    license='LGPLv3',
    url='http://bitbucket.org/cobeio/kube',
    description='Opinionated interface for the Kubernetes API',
    long_description=open('README').read(),
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=CLASSIFIERS,
    keywords='kubernetes k8s watch',
)
