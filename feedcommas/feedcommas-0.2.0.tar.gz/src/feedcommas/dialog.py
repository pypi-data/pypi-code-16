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

'''Separate module for our very special baby: Credentials dialog, which is
displayed before everything.'''

import enum
import urwid

from feedcommas.config import config
from feedcommas.utils import get_password_cmd
from feedcommas.gui_utils import register_palette
from feedcommas.locale import _


class CredEdit(urwid.Edit):
    '''Custom edit box which sends signals on some keypresses.'''
    def __init__(self, *args, **kwargs):
        self._command_map = urwid.command_map.copy()
        self._command_map.restore_defaults()
        super().__init__(*args, **kwargs)

    def keypress(self, size, key):
        return super().keypress(size, key)


class CredPile(urwid.Pile):
    '''Custom pile with added keybindings.'''
    signals = ['done', 'cancel']

    def __init__(self, *args, **kwargs):
        self._command_map = urwid.command_map.copy()
        self._command_map.restore_defaults()
        self._command_map['tab'] = 'cursor down'
        self._command_map['shift tab'] = 'cursor up'
        super().__init__(*args, **kwargs)

    def keypress(self, size, key):
        '''Default actions for enter and escape.'''
        if key not in ('enter', 'esc'):
            return super().keypress(size, key)
        elif super().keypress(size, key) is not None:
            if key == 'enter':
                urwid.emit_signal(self, 'done')
            elif key == 'esc':
                urwid.emit_signal(self, 'cancel')


class CredButton(urwid.Button):
    '''Custom 1-line button which reports its minsize depending on contents.'''
    def __init__(self, *args, **kwargs):
        self._command_map = urwid.command_map.copy()
        self._command_map.restore_defaults()
        super().__init__(*args, **kwargs)

    @property
    def minsize(self):
        '''Returns a minimum needed size for a text + button decorations.'''
        return len(self.get_label()) + 4


class CredButtonDecor(urwid.Columns):
    '''Decorator for buttons which draws all of them on the right, and with
    equal size.'''
    def __init__(self, buttons):
        self._command_map = urwid.command_map.copy()
        self._command_map.restore_defaults()
        self._command_map['tab'] = 'cursor right'
        self._command_map['shift tab'] = 'cursor left'
        minsize = max(btn.minsize for btn in buttons)
        buttons = [(minsize, btn) for btn in buttons]
        buttons.insert(0, urwid.Text(''))  # Moves buttons to the right
        super().__init__(buttons, focus_column=1)


class CredentialsDialog:
    '''Modal dialog which is used to get user credentials when they're not
    set.'''
    class _Exit(Exception):
        def __init__(self, ret):
            self.ret = ret
            super().__init__()

    class Status(enum.Enum):
        '''Codes of clicked buttons.'''
        ok = 0
        cancel = 1

    def __init__(self, provider):
        self._provider = provider

        ok = CredButton(_('Ok'))
        cancel = CredButton(_('Cancel'))

        self.username = CredEdit(_('Name or email: '))
        self.pass_cmd = CredEdit(_('Password command: '))
        self.password = CredEdit(_('Password (plain text, optional): '),
                                 mask='*')
        self.out = urwid.Text('', align='center')

        w = CredPile([
            urwid.Text([('title', _('Log in to CommaFeed'))]),
            urwid.Divider(),
            self.username,
            self.pass_cmd,
            self.password,
            urwid.Divider(),
            self.out,
            urwid.Padding(CredButtonDecor([ok, cancel]), 'right')
        ])

        urwid.connect_signal(w, 'done', self._done)
        urwid.connect_signal(w, 'cancel', self._cancel)

        # pylint: disable=redefined-variable-type
        w = urwid.LineBox(w)
        w = urwid.Padding(w, align='center', width=80)
        w = urwid.Filler(w, valign='middle')

        self.view = w

        urwid.connect_signal(ok, 'click', self._done)
        urwid.connect_signal(cancel, 'click', self._cancel)

        self._loop = urwid.MainLoop(self.view)
        register_palette(self._loop.screen)

    def run(self):
        '''Show a dialog and block until it's finished. Returns a `Status` of
        button which was pressed.'''
        try:
            self._loop.run()
        except CredentialsDialog._Exit as e:
            return e.ret

    def _cancel(self, *args):
        raise CredentialsDialog._Exit(CredentialsDialog.Status.cancel)

    def _done(self, *args):
        username = self.username.get_edit_text()
        if self.pass_cmd.get_edit_text():
            cmd = self.pass_cmd.get_edit_text()
            password = get_password_cmd(cmd, self._log_error)
            if password is None:
                return
        else:
            password = self.password.get_edit_text()

        if username and password:
            self.out.set_text(_('Logging in...'))

            # next call is blocking, so user would never see above text without
            # redrawing screen.
            self._loop.draw_screen()

            if self._provider.change_credentials(username, password):
                server = config()['server']
                server['username'] = self.username.get_edit_text()
                server['password'] = self.password.get_edit_text()
                server['password-cmd'] = self.pass_cmd.get_edit_text()
                raise CredentialsDialog._Exit(CredentialsDialog.Status.ok)
            else:
                self._log_error(_('Incorrect credentials'))
        else:
            self._log_error(_('Please fill credentials'))

    def _log_error(self, text):
        self.out.set_text([('error', text)])
        self._loop.set_alarm_in(3, self._clear_out)

    def _clear_out(self, *args):
        self.out.set_text('')
