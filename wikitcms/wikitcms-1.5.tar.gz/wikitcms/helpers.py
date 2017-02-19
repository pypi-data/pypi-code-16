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
    of calling this directly. Milestones have a letter so they sort
    after nightlies (nightlies are usually going to be earlier).
    """
    s = string.replace('Pre-Alpha', 'f175')
    s = s.replace('Alpha', 'f200')
    s = s.replace('Pre-Beta', 'f375')
    s = s.replace('Beta', 'f400')
    s = s.replace('Preview', 'f600')
    s = s.replace('Pre-Final', 'f775')
    s = s.replace('Final', 'f800')
    s = s.replace('TC', '200')
    s = s.replace('RC', '600')
    return s

def next_composes(milestone, compose):
    """Expects to be fed two strings something like 'Beta', 'TC4',
    identifying a Fedora pre-release compose. Returns a list of tuples
    (milestone, compose) identifying the composes that may plausibly
    follow this one (doesn't handle cases like 'RC1.1'). Returns None
    if fed something it can't make sense of.
    """
    milestones = ['Alpha', 'Beta', 'Final']
    if milestone not in milestones:
        return None
    if compose.find('TC') != 0 and compose.find('RC') != 0:
        return None
    try:
        sep = compose.index('.')
        num = int(compose[2:sep])
    except:
        num = int(compose[2:])
    if compose.find('TC') == 0:
        nextnum = 'TC' + str(num+1)
        nextbump = (milestone, nextnum)
        nextjump = (milestone, 'RC1')
    elif compose.find('RC') == 0:
        nextnum = 'RC' + str(num+1)
        try:
            nextmile = milestones[milestones.index(milestone)+1]
        except:
            # wraparound!
            nextmile = milestones[0]
        nextbump = (milestone, nextnum)
        nextjump = (nextmile, 'TC1')
    else:
        return None
    return [nextbump, nextjump]
