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


from gi.repository import Gtk

import ampd

from gampc import module
from gampc import plugin
from gampc.utils import action
from gampc.utils import omenu
from gampc.utils import ssde

import songlist


class Playlist(songlist.EditableSongList, songlist.SongListWithTotals, module.PanedModule):
    title = _("Playlist Editor")
    name = 'playlist'
    key = '5'

    duplicate_test_columns = ['file']

    def __init__(self, *args, **kwargs):
        super(Playlist, self).__init__(*args, **kwargs)

        self.actions.add_action(action.Action('playlist-rename', self.action_playlist_rename_cb))
        self.actions.add_action(action.Action('playlist-delete', self.action_playlist_delete_cb))

        self.playlist_name = None
        self.modified = False

        self.left_store = Gtk.ListStore()
        self.left_store.set_column_types([str])
        self.left_treeview.set_model(self.left_store)
        self.left_treeview.insert_column_with_attributes(0, '', Gtk.CellRendererPixbuf(icon_name='view-list-symbolic'))
        self.left_treeview.insert_column_with_data_func(1, _("Playlist name"), Gtk.CellRendererText(), self.playlist_name_data_func)
        self.left_treeview.connect('row-activated', self.left_treeview_row_activated_cb)

    def playlist_name_data_func(self, column, renderer, store, i):
        name = store.get_value(i, 0)
        if name == self.playlist_name and self.modified:
            renderer.set_property('text', '* ' + name)
            renderer.set_property('font', 'bold italic')
        else:
            renderer.set_property('text', name)
            renderer.set_property('font', None)

    @ampd.task
    async def client_connected_cb(self, client):
        while True:
            playlists = sorted(map(lambda x: x['playlist'], (await self.ampd.listplaylists())))
            self.left_store_set_rows(playlists)
            self.left_treeview.set_cursor(Gtk.TreePath.new_from_indices([playlists.index(self.playlist_name)]) if self.playlist_name in playlists else Gtk.TreePath.new_first())
            await self.ampd.idle(self.ampd.STORED_PLAYLIST)

    def action_reset_cb(self, action, parameter):
        self.load_playlist()

    def left_treeview_selection_changed_cb(self, *args):
        store, i = self.left_treeview.get_selection().get_selected()
        self.playlist_name = store.get_value(i, 0) if i else None
        self.load_playlist()

    def left_treeview_row_activated_cb(self, left_treeview, p, col):
        self.action_playlist_rename_cb(None, None)

    @ampd.task
    async def load_playlist(self):
        self.set_modified(False)
        if not self.playlist_name:
            self.set_songs([])
            return
        songs = await self.ampd.listplaylistinfo(self.playlist_name)
        self.set_songs(songs)
        self.treeview.get_selection().unselect_all()

    def set_modified(self, modified=True):
        if modified != self.modified:
            self.modified = modified
            self.left_treeview.queue_draw()
        self.treeview.queue_draw()

    @ampd.task
    async def action_save_cb(self, action, parameter):
        tempname = '$$TEMP$$'
        try:
            await self.ampd.playlistclear(tempname)
            await self.ampd.command_list(self.ampd.playlistadd(tempname, song.file) for i, p, song in self.store if song._status != self.SONG_DELETED)
        except:
            await self.ampd.rm(tempname)
            raise
        await self.ampd.command_list((self.ampd.rm(self.playlist_name), self.ampd.rename(tempname, self.playlist_name)))
        self.treeview.get_selection().unselect_all()
        self.load_playlist()

    @ampd.task
    async def action_playlist_rename_cb(self, action, parameter):
        struct = ssde.Text(label=_("Rename playlist"), default=self.playlist_name)
        new_name = struct.dialog(self.win)
        if new_name and new_name != self.playlist_name:
            await self.ampd.rename(self.playlist_name, new_name)
            self.playlist_name = new_name

    @ampd.task
    async def action_playlist_delete_cb(self, action, parameter):
        if not self.playlist_name:
            return
        dialog = Gtk.Dialog(parent=self.win, title=_("Delete playlist"))
        dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        dialog.add_button(_("_OK"), Gtk.ResponseType.OK)
        dialog.get_content_area().add(Gtk.Label(label=_("Delete playlist {name}?").format(name=self.playlist_name), visible=True))
        reply = dialog.run()
        dialog.destroy()
        if reply != Gtk.ResponseType.OK:
            return
        await self.ampd.rm(self.playlist_name)


@ampd.task
async def action_playlist_add_cb(songlist_, action, parameter):
    filenames = songlist_.get_filenames()
    playlists = sorted(map(lambda x: x['playlist'], (await songlist_.ampd.listplaylists())))
    new_playlist = _("<New playlist>")
    struct = ssde.Choice([new_playlist] + playlists,
                         label=_("Add to playlist"))
    value = struct.dialog(songlist_.win)
    if value == new_playlist:
        new_name = _("<New playlist name>")
        struct = ssde.Text(label=_("New playlist name"),
                           default=new_name,
                           validator=lambda x: x != new_name)
        value = struct.dialog(songlist_.win)
    if not value:
        return
    await songlist_.ampd.command_list(songlist_.ampd.playlistadd(value, filename) for filename in filenames)


class PlaylistExtension(plugin.Extension):
    modules = [Playlist]

    def activate(self):
        self.provides['songlist'] = {}
        self.provides['songlist']['actions'] = [action.ActionModel('playlist-add', action_playlist_add_cb)]
        self.provides['songlist']['context_menu_items'] = [omenu.Item('20/10', 'mod.playlist-add', _("Add to playlist"))]

        self.provides[Playlist.name] = {}
        self.provides[Playlist.name]['left_context_menu_items'] = [
            omenu.Item('50/10', 'mod.playlist-rename', _("Rename playlist")),
            omenu.Item('50/20', 'mod.playlist-delete', _("Delete playlist"))
        ]
