########################################################################################
##
## pyKStroke - Simple keyboard input hook on multiple platforms that returns a character.
## Copyright (C) 2014  Tungsteno <contacts00-pykstroke@yahoo.it>
##
## https://bitbucket.org/Tungsteno/pykstroke/wiki/Home
##
## This file is part of pyKStroke.
##
## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public
## License as published by the Free Software Foundation; either
## version 2.1 of the License, or (at your option) any later version.
##
## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with pyKStroke.  If not, see <http://www.gnu.org/licenses/>.
##
########################################################################################

# Distutils installation script for pyKStroke.

#Development status classifiers:
#Development Status :: 1 - Planning
#Development Status :: 2 - Pre-Alpha
#Development Status :: 3 - Alpha
#Development Status :: 4 - Beta
#Development Status :: 5 - Production/Stable
#Development Status :: 6 - Mature
#Development Status :: 7 - Inactive

__version__ = '0.4.0'

cla=[
    'Development Status :: 4 - Beta',
    'Environment :: MacOS X :: Carbon',
    'Environment :: Win32 (MS Windows)',
    'Environment :: X11 Applications',
    'Topic :: System :: Monitoring',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    ]

import sys, os

from setuptools import setup
from setuptools.command.install import install
from cStringIO import StringIO 



if sys.version < '2.3.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.download_url = None 
      
class CustomInstallCommand(install):
    def run(self):
        inst_doc=raw_input("Would you like to even install the DOCS folder? [Yes/No](Yes)")  
        inst_doc=inst_doc.lstrip()
        inst_doc=inst_doc.rstrip()
        inst_doc=inst_doc.lower()
        if (inst_doc!="y" and inst_doc!="yes" and inst_doc!=""):
            self.distribution.package_data={}
        install.run(self)

file_path = os.path.realpath(os.path.dirname(__file__))

readme_path = os.path.join(file_path, 'pyKStroke/docs/')
readme_md, readme_rst = 'README.md', 'README.rst'

#extract description paragraph from README.md
with open(os.path.join(readme_path,readme_md), 'r') as file:
    file_cont = file.read()
cont_indesc = file_cont.split("##Description",1)[1]
long_desc = cont_indesc.split("---",1)[0]
__desc__ = long_desc.split("####",1)[1]
__desc__ = __desc__.split("\n",1)[0]

try:
    import pypandoc
    print "converting README from markdown to restructuredtext..."
    __long_desc__ = pypandoc.convert_text(long_desc,'rst',format='md',extra_args=['--wrap=preserve'])
except ImportError:
    print "skipping README conversion..."
    __long_desc__ = long_desc

setup(
    name = 'pyKStroke',
    version = __version__,
    description = __desc__,
    long_description = __long_desc__,
    author = 'Tungsteno',
    author_email = 'contacts00-pykstroke@yahoo.it',
    url = 'https://bitbucket.org/Tungsteno/pykstroke/wiki/Home',
    packages = ["pyKStroke",'pyKStroke.ksSystem','pyKStroke.ksApplication'],
    cmdclass = {'install': CustomInstallCommand},
    package_data = {"": ["docs/LICENSE","docs/README.md","docs/README.rst","docs/Reference.md"]},                  
    extras_require = {
        ":sys_platform=='win32'": [
            'pypiwin32>=218',
            'pyWinhook>=1.5.2',
        ],
        ":sys_platform=='linux2'": [
            'python-xlib>=0.16',
        ],
        ":sys_platform=='darwin'": [
            'python-xlib>=0.16',
        ],
    },    
    download_url = ''.join(('https://bitbucket.org/Tungsteno/pykstroke/get/', __version__, '.zip')), 
    license = 'LGPLv2.1+',
    keywords = 'input keyboard system events user control hook',
    classifiers = cla
)

