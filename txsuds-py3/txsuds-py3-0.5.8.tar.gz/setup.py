#!/usr/bin/python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )

from setuptools import setup, find_packages

package_name = "txsuds-py3"
package_version = '0.5.8'

setup(
    name=package_name,
    provides="txsuds",
    version=package_version,
    description="Lightweight SOAP client for Twisted + Py3",
    author="Jeff Ortel",
    author_email="jortel@redhat.com",
    maintainer="Synerty",
    maintainer_email="contact@synerty.com",
    packages=find_packages(exclude=['tests']),
    url="https://github.com/Synerty/txsuds-py3",
)
