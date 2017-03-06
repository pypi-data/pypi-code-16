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

from enum import Enum
import urwid


class Level(Enum):
    info = 1
    error = 2


class cli_log(metaclass=urwid.signals.MetaSignals):
    '''The idea is to allow everyone logging error messages to the commandline.
    To achieve it we need an object which can be connected with commandline and
    will send signals when requested.'''
    signals = ['log']

    def info(self, text):
        urwid.emit_signal(self, 'log', Level.info, text)

    def error(self, text):
        urwid.emit_signal(self, 'log', Level.error, text)


log = cli_log()
