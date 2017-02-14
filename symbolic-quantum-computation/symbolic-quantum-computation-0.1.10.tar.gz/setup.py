from distutils.core import setup

setup(
    # Application name:
    name='symbolic-quantum-computation',

    # Version number (initial):
    version='0.1.10',

    # Application author details:
    author='Nikita',
    author_email='email@addr.ess',

    # Packages
    packages=['sqc', 'unit_test'],   # SymbolicQuantumComputation
    entry_points={
        'console_scripts': [
            'sqc = sqc.__main__:main',
            'sqc.run_tests = unit_test.__main__:main'
        ]
    },


    # Include additional files into the package
    include_package_data=True,

    # Details
    url='https://bitbucket.org/grpdev/symbolic-quantum-computation',

    #
    license='LICENSE.txt',
    readme='README.txt',
    description='symbolic-quantum-computation description',

    # long_description=open('README.txt').read(),

    # Dependent packages (distributions)
    install_requires=[
        'numpy'
    ],
    requires=[
        'src',
    ]
)
