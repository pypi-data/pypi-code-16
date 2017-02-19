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

import re

MILESTONE_PAIRS = (
    ('Rawhide', 'f100'),
    # These two are kinda the same, we called Branched nightly pages
    # 'Nightly' in F21 cycle
    ('Branched', 'f150'),
    ('Nightly', 'f150'),
    ('Pre-Alpha', 'f175'),
    ('Alpha', 'f200'),
    ('Pre-Beta', 'f375'),
    ('Beta', 'f400'),
    ('Preview', 'f600'),
    ('Pre-Final', 'f775'),
    ('Final', 'f800'),
)

COMPOSE_PAIRS = (
    ('TC', '200'),
    ('RC', '600'),
)

def fedora_release_sort(string):
    """Fed a string that looks something like a Fedora pre-release /
    compose version, this will output a modified version of the string
    which should sort correctly against others like it. Handles stuff
    like 'Preview' coming before 'Final', and 'TC' coming before 'RC'.
    'Alpha', 'Beta' and 'Final' sort correctly by pure chance, but we
    handle them here anyway to make sure. wikitcms ValidationEvent and
    ValidationPage objects have a 'sortname' property you can use
    instead of calling this directly. Milestones have a letter so they
    sort after nightlies (nightlies are usually going to be earlier).
    NOTE: can only sort compose event versions, really. With this
    function, '22 Alpha TC1' > '22 Alpha'.
    """
    for (orig, repl) in MILESTONE_PAIRS + COMPOSE_PAIRS:
        string = string.replace(orig, repl)
    return string

def fedora_release_unsort(string):
    """Does the reverse of fedora_release_sort. Because I designed
    fedora_release_sort badly and can't really escape from it easily
    this might not always work 100%, but for common cases it should
    give you something you can turn back into a (release, milestone,
    compose) triple easily enough.
    """
    for (repl, orig) in MILESTONE_PAIRS + COMPOSE_PAIRS:
        string = string.replace(orig, repl)
    return string

def triplet_sort(release, milestone, compose):
    """Just like fedora_release_sort, but requires you to pass the
    now-'standard' release, milestone, compose triplet of inputs.
    This is a better way in most cases as you're going to have more
    certainty about instantiating wikitcms/fedfind objects from it,
    plus we can handle things like '23' being higher than '23 Beta'
    or '23 Final TC1'.
    """
    for (orig, repl) in MILESTONE_PAIRS:
        milestone = milestone.replace(orig, repl)
        if not milestone:
            # ('23', 'Final', '') == ('23', '', '')
            milestone = 'f800'
    for (orig, repl) in COMPOSE_PAIRS:
        compose = compose.replace(orig, repl)
        if not compose:
            compose = '999'
    return (release, milestone, compose)

def triplet_unsort(release, milestone, compose):
    """Reverse of triplet_sort."""
    for (repl, orig) in MILESTONE_PAIRS:
        milestone = milestone.replace(orig, repl)
        if milestone == 'f800':
            milestone = 'Final'
    for (repl, orig) in COMPOSE_PAIRS:
        compose = compose.replace(orig, repl)
        if compose == '999':
            compose = ''
    return (release, milestone, compose)

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

def rreplace(string, old, new, occurrence):
    """A version of the str.replace() method which works from the right.
    Taken from https://stackoverflow.com/questions/2556108/
    """
    li = string.rsplit(old, occurrence)
    return new.join(li)

def normalize(text):
    """Lower case and replace ' ' with '_' so I don't have to
    keep retyping it.
    """
    return text.lower().replace(' ', '_')

def find_bugs(text):
    """Find RH bug references in a given chunk of text. More than one
    method does this, so we'll put the logic here and they can share
    it. Copes with [[rhbug:(ID)]] links, {{bz|(ID)}} templates and
    URLs that look like Bugzilla. Doesn't handle aliases (only matches
    numeric IDs 6 or 7 digits long). Returns a set (so bugs that occur
    multiple times in the text will only appear once in the output).
    """
    bugs = set()
    bzpatt = re.compile(r'({{bz *\| *|'
                        '\[\[rhbug *: *|'
                        'bugzilla\.redhat\.com/show_bug\.cgi\?id=)'
                        '(\d{6,7})')
    matches = bzpatt.finditer(text)
    for match in matches:
        bugs.add(match.group(2))
    # Filter out bug IDs usually used as examples
    for bug in ('12345', '123456', '54321', '654321', '234567', '1234567',
               '7654321'):
        bugs.discard(bug)
    return bugs
