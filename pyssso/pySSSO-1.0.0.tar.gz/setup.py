
from setuptools import setup

setup(
    name='pySSSO',
    version='1.0.0',
    author='Jules Kouatchou',
    author_email='Jules.Kouatchou-1@nasa.gov',
    packages=['pySSSO', 'pySSSO.fsrc', 'pySSSO.ioUtils', 'pySSSO.stationPlottingTool', 'pySSSO.tests', 'pySSSO.viz', 'pySSSO.utils'],
    url='https://pypi.python.org/pypi/pySSSO/',
    license='LICENSE.txt',
    description='Useful script to manipulate data and visualize them.',
    long_description=open('README.txt').read(),
    install_requires=[
       'netCDF4',
       'numpy',
       'matplotlib',
       'cartopy',
       'mpl_toolkits',
    ],
)
