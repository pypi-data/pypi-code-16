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

'''Man entry point'''

import os
import sys
import atexit
import logging
import argparse
import urwid

import feedcommas.config as config
import feedcommas.content as content
import feedcommas.widgets as widgets
import feedcommas.dialog as dialog
import feedcommas.actions as actions
import feedcommas.cache as cache
from feedcommas.key import Key
from feedcommas.utils import eprint
from feedcommas.gui_utils import register_palette
from feedcommas.locale import _
from feedcommas._version import version


log = logging.getLogger('feedcommas')


def quit_():
    '''Quit main loop'''
    raise urwid.ExitMainLoop()


def set_title(title):
    '''Set a title of terminal window. The codes accepted by terminals and
    terminal multiplexers were found in Weechat's source code.
    (src/gui/curses/gui-curses-window.c).
    Weechat is free software, licensed under GNU GPL v3+.'''
    if not title:
        return

    term = os.getenv('TERM')

    if not term:
        return

    xterm_like = ['xterm', 'rxvt', 'Eterm', 'aixterm', 'iris-ansi', 'dtterm']
    multiplexers = ['screen', 'tmux']

    if term.startswith('sun-cmd'):
        sys.stdout.write("\033k%s\033\\" % title)
        return True
    elif term.startswith('hpterm'):
        sys.stdout.write("\033&f0k%dD%s" % (len(title) + 1, title))
        return True
    elif any(term.startswith(check) for check in xterm_like):
        sys.stdout.write("\33]0;%s\7" % title)
        return True
    elif any(term.startswith(check) for check in multiplexers):
        sys.stdout.write("\033k%s\033\\" % title)
        return True


def clear_title():
    '''Clears title set on program start to the currently running shell name.'''
    term = os.getenv('TERM')
    title = os.path.basename(os.getenv('SHELL'))
    if not term:
        return
    if not title:
        title = term

    multiplexers = ['screen', 'tmux']

    if any(term.startswith(check) for check in multiplexers):
        sys.stdout.write("\033k%s\033\\" % title)


def unhandled_handler(key):
    '''Input not handled otherwise. Can be either keypress or mouse even (in
    which case Key() will raise TypeError because some of operations on expected
    string will fail)'''
    if urwid.command_map[key] == 'quit':
        quit_()


def register_keys(keys):
    '''Register user-specified keys to urwid's command map.'''
    cmds = actions.CommandMapping()
    for action_name, key in keys.items():
        urwid_name = cmds[action_name]
        urwid.command_map.clear_command(urwid_name)
        urwid.command_map[str(Key(key))] = cmds[action_name]


def register_global_commands(cmd_handler):
    '''Register commands available from everywhere.'''
    cmd_handler.register_action('quit', quit_)


def parse_args():
    '''Support for commanline arguments.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default=None,
                        help='path to the configuration file')

    parser.add_argument('--version', action='version',
                        version='%(prog)s %(version)s' %
                        {'prog': '%(prog)s', 'version': version})
    return parser.parse_args()


def main():
    args = parse_args()

    if args.config:
        try:
            # no os.path.expanduser(args.config) on purpose:
            # feed-commas -c "~/blah" shouldn't expand a tilde to $HOME. Leave
            # that to user's shell.
            config.set_path(args.config)
        except config.ConfigNotWritable:
            eprint(_('Configuration not writable: %s') % args.config)
            return 1

    cfg = config.config()
    atexit.register(config.write_config, cfg)

    if set_title(cfg['settings']['window-title']):
        atexit.register(clear_title)

    cache.init()
    register_keys(cfg['keys'])

    cmd_handler = actions.CommandHandler()
    register_global_commands(cmd_handler)

    urwid_loop = urwid.MainLoop(None, unhandled_input=unhandled_handler)

    register_palette(urwid_loop.screen)

    with content.make_provider(urwid_loop, cfg['server']) as cp:
        sv = cfg['server']
        if not sv['username'] and not sv['password'] and not sv['password-cmd']:
            cancel = dialog.CredentialsDialog.Status.cancel
            if dialog.CredentialsDialog(cp).run() == cancel:
                return 1

        urwid_loop.widget = widgets.MainWindow(cp, urwid_loop, cmd_handler)
        urwid_loop.run()
