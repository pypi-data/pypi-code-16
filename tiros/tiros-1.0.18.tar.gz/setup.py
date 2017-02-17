from setuptools import setup

setup(
    name='tiros',
    version='1.0.18',
    packages=['tiros'],
    install_requires=['requests>=2.11.1', 'boto3>=1.4.4', 'datetime>=4.1.1'],
    entry_points={
        'console_scripts': [
            'tiros = tiros.cli:main',
        ],
    },
)
