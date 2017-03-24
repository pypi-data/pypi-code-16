"""A corpus of object images."""

from setuptools import setup


setup_args = dict(
    name='objects',
    packages=['objects'],
    version="0.3.0",
    description='A corpus of object images',
    url='http://github.com/suchow/Objects',
    maintainer='Jordan Suchow',
    maintainer_email='suchow@berkeley.edu',
    keywords=['objects'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    zip_safe=False,
)

setup(**setup_args)
