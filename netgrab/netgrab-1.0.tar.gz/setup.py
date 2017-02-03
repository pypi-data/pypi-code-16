"""
NetGrab
------------
NetGrab Focuses on adding simplicity to getting basic dns information
"""

from setuptools import setup

setup(
    name='netgrab',
    version='1.0',
    url='https://github.com/z4y/netgrab',
    license='GNU',
    author='Cameron Poe',
    author_email='cameron@zay.li',
    description='Add simplicity to getting basic dns information',
    long_description=__doc__,
    py_modules=['netgrab'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['dnspython', 'cymruwhois'],
)
