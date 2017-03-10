# Copyright (C) 2017 Michał Góral.
#
# This file is part of Feed Commas
#
# Feed Commas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feed Commas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Feed Commas. If not, see <http://www.gnu.org/licenses/>.

'''Utilities for uniform handling of user input.'''

import re
import functools

from collections import OrderedDict

_modmap = OrderedDict((('a', 'meta'),
                       ('c', 'ctrl'),
                       ('s', 'shift')))

_escm = dict((re.escape('%s-' % k), '%s ' % v) for k, v in _modmap.items())
_repl = re.compile('|'.join(_escm.keys()))


@functools.total_ordering
class Key:
    '''Abstraction over a key description which glues together feedcommas' and
    urwid's way of describing keybindings. It ensures that returned key string's
    modifiers are always in the same order, so they can be correctly hashed and
    searched.'''
    def __init__(self, keystr=None):
        self.key = ''

        for modname in _modmap.values():
            setattr(self, modname, False)

        if keystr:
            keystr = _repl.sub(lambda m: _escm[re.escape(m.group(0))], keystr)
            norm_keys = []
            for key in keystr.split():
                if key in _modmap.values():
                    setattr(self, key, True)
                else:
                    norm_keys.append(key)
            self.key = ' '.join(norm_keys)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return str(self) == str(other)

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        ret = ''
        for modname in _modmap.values():
            if getattr(self, modname):
                ret += '%s ' % modname
        ret += self.key
        return ret

    def __repr__(self):
        return 'Key(%s)' % str(self)
