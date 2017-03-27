from setuptools import setup
from os import path

generator_root = path.join('pypass', 'generator')

setup(
    name='pypass-generator',
    version='0.2',
    packages=['pypass', 'pypass.generator', 'pypass.passphrase'],
    # data_files=[(generator_root, [path.join(generator_root, 'diceware.sqlite')])],
    package_data={'pypass.generator': ['diceware.sqlite']},
    include_package_data=True,
    install_requires=['requests>=2.12.5'],
    url='https://bitbucket.org/darrenpmeyer/pypass-generator',
    license='License :: OSI Approved :: Apache Software License',
    author='Darren P Meyer',
    author_email='darren@darrenpmeyer.com',
    description='Password and Passphrase Generator using Diceware and other sources'
)
