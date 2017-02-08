from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

requirements = (
    'path.py >= 7.0',
    'numpy >= 1.8',
    'scipy >= 0.14',
    'configobj >= 5.0',
    'click >= 5.1',
    'requests >= 2.4',
    'prody'
)

scripts = (
    'scripts/cl_load_job',
    'scripts/cluspro_local.py',
)

with open(path.join(here, "README.rst")) as f:
    long_description = f.read()

setup(
    name="sblu",
    packages=['sblu', 'sblu.cli',
              'sblu.cli.docking', 'sblu.cli.pdb',
              'sblu.cli.measure', 'sblu.cli.cluspro',
              'sblu.cli.ftmap'],
    description="Library for munging data files from ClusPro/FTMap/etc.",
    long_description=long_description,
    url="https://bitbucket.org/bu-structure/sb-lab-utils",
    author="Bing Xia",
    author_email="sixpi@bu.edu",
    license="MIT",
    install_requires=requirements,

    use_scm_version={'write_to': 'sblu/version.py'},
    setup_requires=['setuptools_scm'],

    scripts=scripts,
    entry_points={
        'console_scripts': [
            "sblu = sblu.cli.main:cli",
            # Prep commands
            "pdbclean = sblu.cli.pdb.cmd_clean:cli",
            "pdbprep = sblu.cli.pdb.cmd_prep:cli",
            # RMSD commands
            "srmsd = sblu.cli.measure.cmd_srmsd:cli",
            "pypwrmsd = sblu.cli.measure.cmd_pwrmsd:cli",
            "ftrmsd = sblu.cli.measure.cmd_ftrmsd:cli"
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    keywords='cluspro protein PDB',
    use_2to3=True
)
