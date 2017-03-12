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

'''Collection of useful functions related to creating and managing user
interface.'''

import urwid

from feedcommas.config import config


def register_palette(screen):
    '''Intelligently registers user-defined colors as screen's palette.'''
    cols = config()['colors']

    _register_pentry(screen, None, '', '')
    _register_pentry(screen, 'reverse', 'standout', '')
    _register_pentry(screen, 'title', cols['article-title'], '')
    _register_pentry(screen, 'article', '', '')
    _register_pentry(screen, 'metadata', cols['metadata'], '')
    _register_pentry(screen, 'line', '', '')
    _register_pentry(screen, 'menu item', '', '')
    _register_pentry(screen, 'menu indent', '', '')
    _register_pentry(screen, 'menu selected', cols['menu-selected'], '')
    _register_pentry(screen, 'menu line', cols['menu-line'], '')
    _register_pentry(screen, 'log', '', '')
    _register_pentry(screen, 'error', cols['error-fg'], cols['error-bg'])
    _register_pentry(screen, 'focus title', cols['article-title-focus'], '')
    _register_pentry(screen, 'focus article', '', '')
    _register_pentry(screen, 'focus line', cols['article-border-focus'], '')
    _register_pentry(screen, 'focus menu item',
                     cols['menu-focus-fg'], cols['menu-focus-bg'])

    screen.set_terminal_properties(
        colors=config()['settings'].getint('supported-colors'),
        bright_is_bold=config()['settings'].getboolean('bright-bold'))


def _register_pentry(screen, name, fg, bg):
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
