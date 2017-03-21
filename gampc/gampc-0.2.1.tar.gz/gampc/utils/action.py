# coding: utf-8
#
# Graphical Asynchronous Music Player Client
#
# Copyright (C) 2015 Itaï BEN YAACOV
#
# This program is free software: you can redistribute it and/or modify
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


from gi.repository import GObject, Gio


class Action(Gio.SimpleAction):
    def __init__(self, name, activate_cb=None, unsafe=False, shared=None, *args, **kwargs):
        super().__init__(name=name, *args, **kwargs)
        if activate_cb:
            self.connect('activate', activate_cb)
        if unsafe:
            shared.bind_property('safe-mode', self, 'enabled', GObject.BindingFlags.SYNC_CREATE, lambda x, y: not y)


class ActionModel(object):
    def __init__(self, name, activate_cb, *args, **kwargs):
        self.name = name
        self.activate_cb = activate_cb
        self.args = args
        self.kwargs = kwargs

    def create_action(self, decorator, **kwargs):
        return Action(self.name, decorator(self.activate_cb), *self.args, **self.kwargs, **kwargs)

    def get_name(self):
        return self.name


class PropertyAction(Gio.PropertyAction):
    def __init__(self, name, object, *args, **kwargs):
        super().__init__(name=name, object=object, property_name=name, *args, **kwargs)
