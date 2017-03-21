from setuptools import setup, find_packages

install_requires = []
tests_require = ['pytest', 'pytest-runner>=2.0,<3dev', 'pytest-flake8']

setup(
    name='presslabs-sugar',
    version='1.0.0',
    description="Various sugars and goodies for projects.",
    long_description=open('README.rst', 'r').read(),
    license="MIT",
    author="Presslabs SRL",
    author_email="ping@presslabs.com",
    url="https://github.com/PressLabs/sugar",
    install_requires=install_requires,
    tests_require=tests_require,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    extras_require={
        'test': tests_require
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ]
)
