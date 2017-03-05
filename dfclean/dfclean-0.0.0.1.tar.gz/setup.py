from distutils.core import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='dfclean',
    version='0.0.0.1',
    packages=['dfclean'],
    url='https://gitlab.com/panter_dsd/distfilescleaner',
    license='GPLv3',
    author='PanteR',
    author_email='panter.dsd@gmail.com',
    description='Clean up old distfiles in Gentoo',
    long_description=long_description,
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
    ]
)
