from distutils.core import setup

setup(
    # Application name:
    name='symbolic-quantum-computation',

    # Version number (initial):
    version='0.1.17',

    # Application author details:
    author='Nikita',
    author_email='email@addr.ess',

    # Packages
    packages=['sqc', 'src', 'test_package'],   # SymbolicQuantumComputation
    entry_points={
        'console_scripts': [
            'sqc = sqc.__main__:main'
        ]
    },
    py_modules=[

    ],


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

    ]
)
