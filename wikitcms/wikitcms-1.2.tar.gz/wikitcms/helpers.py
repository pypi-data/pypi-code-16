# Copyright (C) 2014 Red Hat
#
# This file is part of wikitcms.
#
# wikitcms is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>
#
# This page contains helper functions that don't strictly belong in any
# particular class or even in another file but outside of a class.

def fedora_release_sort(string):
    """Fed a string that looks something like a Fedora pre-release /
    compose version, this will output a modified version of the string
    which should sort correctly against others like it. Handles stuff
    like 'Preview' coming before 'Final', and 'TC' coming before 'RC'.
    'Alpha', 'Beta' and 'Final' sort correctly by pure chance, but we
    handle them here anyway to make sure. tcmswiki ComposeEvent and
    ComposePage objects have a 'sortname' property you can use instead
    of calling this directly.
    """
    s = string.replace('Pre-Alpha', '175')
    s = s.replace('Alpha', '200')
    s = s.replace('Pre-Beta', '375')
    s = s.replace('Beta', '400')
    s = s.replace('Preview', '600')
    s = s.replace('Pre-Final', '775')
    s = s.replace('Final', '800')
    s = s.replace('TC', '200')
    s = s.replace('RC', '600')
    return s
