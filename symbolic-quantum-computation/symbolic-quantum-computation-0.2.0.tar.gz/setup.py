from distutils.core import setup




setup(
    # Application name:
    name='symbolic-quantum-computation',

    # Version number (initial):
    version='0.2.0',

    # Application author details:
    author='Savelyev Nikita',
    author_email='savelyevno@gmail.com',

    # Packages
    packages=['sqc', 'src', 'test_package'],   # sqc stands for SymbolicQuantumComputation
    entry_points={
        'console_scripts': [
            'sqc = sqc.__main__:main'
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
    ]
)
