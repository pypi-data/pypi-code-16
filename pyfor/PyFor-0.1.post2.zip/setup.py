from distutils.core import setup

setup(
    name='PyFor',
    version='0.1.post2',
    author='Bryce Frank',
    author_email='bryce.frank@oregonstate.edu',
    packages=['PyFor'],
    url='https://github.com/brycefrank/pyfor',
    license='LICENSE.txt',
    install_requires=[
        'numpy',
        'numpy-mkl',
        'gdal',
        'ogr',
        'affine',
        'numpy-mkl',
        'scipy',
        'pandas',
        ],
    dependency_links = ['http://github.com/brycefrank/laspy/tarball/master#egg=laspy-1.3.0'],
    description='Tools for forest resource LiDAR.',
)
