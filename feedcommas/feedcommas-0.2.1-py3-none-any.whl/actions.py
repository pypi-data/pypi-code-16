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

'''Code related to generic handling of actions supported by Feed Commas.

Actions are, more-less, options defined by a user in [keys] section of
configuration file, but in fact they're all the keys defined in urwid's
command_map.'''

import collections


class CommandMapping:
    '''Feed Commas to urwid map of command names.'''
    _mapping = {
        'nav-up': 'cursor up',
        'nav-down': 'cursor down',
        'nav-left': 'cursor left',
        'nav-right': 'cursor right',
    }

    def __getitem__(self, name):
        '''Returns mapped command names and original name if it isn't mapped to
        anything.'''
        ret = self._mapping.get(name)
        if ret is not None:
            return ret
        return name


class UnhandledAction(Exception):
    '''Base class of exceptions called when handling action is impossible.'''
    pass


def handle_key(key, actions, cmd_map, default=None):
    '''Handles a given key according to the rules of a `actions` dictionary and
    urwid's command map (`cmd_map`). If a given key cannot be handled, calls
    returns `default()` or a key otherwise (according to urwid rules of handling
    keypresses).'''
    action_name = cmd_map[key]
    try:
        return handle_action(action_name, actions, cmd_map)
    except UnhandledAction:
        if default is not None:
            return default()
        return key


def handle_action(action_name, actions, cmd_map, default=None):
    '''Call an action with a given name from actions map. If it's impossible to
    call any action, raises UnhandledAction exception.'''
    action = actions.get(action_name, default)
    if action is not None:
        return action()
    raise UnhandledAction(action_name)


class CommandHandler:
    '''CommandHandler'''
    def __init__(self):
        self._action_handlers = collections.defaultdict(list)

    def register_action(self, name, fn):
        '''Register action under a given name as a valid command.'''
        self._action_handlers[name].append(fn)

    def register_actions(self, action_mapping, obj):
        '''Register multiple actions at once. `action_mapping` is a dict-like
        object.'''
        for name, fn in action_mapping.items():
            self.register_action(name, fn)

    def get_abbrev_names(self, abbrev):
        '''Get command names among registered commands which start with a given
        abbreviation.'''
        return [regname for regname in self._action_handlers
                if regname.startswith(abbrev)]

    def call(self, action_name):
        '''Call action with a given name. If exact action isn't found, its
        abbreviation is called, but only when there exists exactly one (i.e.
        it's unambiguous).'''
        # defaultdict.get doesn't automatically create handler name
        fns = self._action_handlers.get(action_name)
        if fns:
            self._call(fns)
        else:
            names = self.get_abbrev_names(action_name)
            if len(names) == 1:
                self._call(self._action_handlers[names[0]])

    def _call(self, fns):
        for fn in fns:
            fn()
