from setuptools import setup
from setuptools import find_packages

setup(
    name="GPRas",

    version="0.1.0",
    
    author="Benny Chin",
    author_email="wcchin.88@gmal.com",

    packages=['GPRas', 'GPRas.GPRa', 'GPRas.GPRa.input_funcs', 'GPRas.GPRa.output_funcs'],

    include_package_data=True,

    url="https://bitbucket.org/wcchin/gpras",

    # license="LICENSE.txt",
    description="algorithms for measuring concentration distribution in a spatial network.",

    # long_description=open("README.txt").read(),
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',

         'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
    ],

    keywords='spatial network concentration',

    install_requires=[
        "numpy",
        "pandas",
        "geopandas",
        "shapely",
        "networkx",
    ],
)
