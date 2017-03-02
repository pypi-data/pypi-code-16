# cykooz.recipe.wsgi
# Copyright (C) 2017 Cykooz
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from setuptools import setup, find_packages


setup(
    name='cykooz.recipe.wsgi',
    version='1.0.0',
    url='https://bitbucket.org/cykooz/cykooz.recipe.wsgi',
    license='GPL 2',
    author='Cykooz',
    author_email='saikuz@mail.ru',
    description='This recipe for zc.buildout creates a script that can be used as an entry point for WSGI servers.',
    long_description=(
        open('README.txt').read() + '\n\n' +
        open('CHANGES.txt').read()
    ),
    classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['cykooz', 'cykooz.recipe'],
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
    ],
    extras_require={
        'test': []
    },
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'zc.buildout': [
            'default = cykooz.recipe.wsgi:Recipe',
        ]
    }
)
