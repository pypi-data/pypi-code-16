from setuptools import setup
from setuptools.command import sdist
import sys

if sys.version < '2.7':
    sys.exit("Sorry, Python >= 2.7 is required for this application.")


setup(
    name = "ameba",
    version = "1.0",
    description = "AMEBA: Advanced MEtabolic Branchpoint Analysis",
    author = "Rene Rex, Alexander Riemer and Julia Helmecke",
    author_email = "j.helmecke@tu-bs.de",
    url='http://metano.tu-bs.de/ameba',
    package_dir={"ameba": "src"},
    packages = ["ameba"],
    package_data={
        "ameba" : ["example/*.txt", "example/*.ini", "example/*.sh", "gpl.txt", "xdot.py"]
        },
    entry_points = {
      "console_scripts": [
         'ameba = ameba.ameba:main']
    },
    classifiers = [
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    keywords = "genome-scale metabolic models flux balance analysis",
    license = "GPL",
    install_requires = [
        "setuptools",
        "pygobject",
        "metano",
        "networkx>=1.7",
        "pygraphviz>=1.1",
    ],
)
