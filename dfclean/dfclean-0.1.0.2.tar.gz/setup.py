from distutils.core import setup

setup(
    name='dfclean',
    version='0.1.0.2',
    packages=['dfclean'],
    url='https://gitlab.com/panter_dsd/distfilescleaner',
    license='GPLv3',
    author='PanteR',
    author_email='panter.dsd@gmail.com',
    description='Clean up old distfiles in Gentoo',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 4.6',
    ],
    requires=['humanize']
)
