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

import atexit
import logging
import urwid

import feedcommas.config as config
import feedcommas.content as content
import feedcommas.widgets as widgets
import feedcommas.actions as actions
import feedcommas.cache as cache
from feedcommas.key import Key


log = logging.getLogger('feedcommas')

def quit_():
    raise urwid.ExitMainLoop()

def unhandled_handler(key):
    '''Input not handled otherwise. Can be either keypress or mouse even (in
    which case Key() will raise TypeError because some of operations on expected
    string will fail)'''
    if urwid.command_map[key] == 'quit':
        quit_()

def register_pentry(screen, name, fg, bg):
    '''Intelligently registers palette entry. First tries to register fg and bg
    as 16-color palette, optionally with support for monochrome terminals, and
    if it doesn't work, falls back to registering in 256 high color mode.'''
    try:
        if fg:
            screen.register_palette_entry(name, fg, bg, mono=fg)
        elif bg:
            screen.register_palette_entry(name, fg, bg, mono=bg)
    except urwid.display_common.AttrSpecError:
        try:
            screen.register_palette_entry(name, fg, bg)
        except urwid.display_common.AttrSpecError:
            screen.register_palette_entry(name, '', '', None, fg, bg)


def register_keys(keys):
    cmds = actions.CommandMapping()
    for action_name, key in keys.items():
        urwid_name = cmds[action_name]
        urwid.command_map.clear_command(urwid_name)
        urwid.command_map[str(Key(key))] = cmds[action_name]


def register_global_commands(cmd_handler):
    cmd_handler.register_action('quit', quit_)


def main():
    cfg = config.config()
    atexit.register(config.write_config, cfg)
    cache.init()
    register_keys(cfg['keys'])

    cmd_handler = actions.CommandHandler()
    register_global_commands(cmd_handler)

    urwid_loop = urwid.MainLoop(None, unhandled_input=unhandled_handler)

    cols = cfg['colors']
    scr = urwid_loop.screen
    scr.set_terminal_properties(
        colors=cfg['settings'].getint('supported-colors'),
        bright_is_bold=cfg['settings'].getboolean('bright-bold'))

    register_pentry(scr, None, '', '')
    register_pentry(scr, 'reverse', 'standout', '')
    register_pentry(scr, 'title', cols['article-title'], '')
    register_pentry(scr, 'article', '', '')
    register_pentry(scr, 'metadata', cols['metadata'], '')
    register_pentry(scr, 'line', '', '')
    register_pentry(scr, 'menu item', '', '')
    register_pentry(scr, 'menu indent', '', '')
    register_pentry(scr, 'menu selected', cols['menu-selected'], '')
    register_pentry(scr, 'menu line', cols['menu-line'], '')
    register_pentry(scr, 'log', '', '')
    register_pentry(scr, 'error', cols['error-fg'], cols['error-bg'])
    register_pentry(scr, 'focus title', cols['article-title-focus'], '')
    register_pentry(scr, 'focus article', '', '')
    register_pentry(scr, 'focus line', cols['article-border-focus'], '')
    register_pentry(scr, 'focus menu item', cols['menu-focus-fg'],
                                             cols['menu-focus-bg'])

    with content.make_provider(urwid_loop, cfg['server']) as cp:
        urwid_loop.widget = widgets.MainWindow(cp, urwid_loop, cmd_handler)
        urwid_loop.run()
