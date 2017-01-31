#
#    Uncomplicated VM Builder
#    Copyright (C) 2007-2009 Canonical Ltd.
#
#    See AUTHORS for list of contributors
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3, as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

class Suite(object):
    def __init__(self, context):
        self.context = context
        self.isodir = '/media/vmbuilder_inst_image'
        self.iso_mounted = False

    def check_arch_validity(self, arch):
        """Checks whether the given arch is valid for this suite"""
        raise NotImplemented('Suite subclasses need to implement the check_arch_validity method')
