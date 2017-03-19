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


from gi.repository import GObject, GLib, Gdk, Gtk, Pango
import re
import ast
import cairo


def format_time(time):
    time = int(time)
    hours = time // 3600
    minutes = (time // 60) % 60
    seconds = time % 60
    return '{:d}:{:02d}:{:02d}'.format(hours, minutes, seconds) if hours else '{:d}:{:02d}'.format(minutes, seconds)


def store_set_rows(store, rows, func):
    if not rows:
        store.clear()
        return
    i = store.get_iter_first()
    appending = (i is None)
    for row in rows:
        if appending:
            i = store.append()
        func(i, row)
        if not appending:
            i = store.iter_next(i)
            if i is None:
                appending = True
    if not appending:
        while store.remove(i):
            pass


def config_notify_cb(obj, param, config):
    config[param.name] = obj.get_property(param.name)


class Field(GObject.GObject):
    title = GObject.property(type=str)
    width = GObject.property(type=int)
    visible = GObject.property(type=bool, default=True)
    xalign = GObject.property(type=float, default=0.0)

    get_value = None

    def __init__(self, name, title=None, min_width=50, get_value=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.title = title
        self.width = self.min_width = min_width
        if get_value:
            self.get_value = get_value

    def get_renderer(self):
        return Gtk.CellRendererText(ellipsize=Pango.EllipsizeMode.END, xalign=self.xalign)

    def __repr__(self):
        return "Field '{title}'".format(title=self.title)


class FieldWithTable(Field):
    def __init__(self, name, title=None, table=None, min_width=50, **kwargs):
        super(FieldWithTable, self).__init__(name, title, min_width, **kwargs)
        self.table = table

    def get_value(self, song):
        for field, pattern, value in self.table:
            if not field:
                return value
            else:
                match = re.search(pattern, song.get(field, ''))
                if match:
                    return match.expand(value)


class FieldFamily(GObject.GObject):
    order = GObject.property()

    def __init__(self, config):
        super(FieldFamily, self).__init__()
        self.config = config
        self.old_info = self.config.get('info', {})
        self.old_order = self.config.get('order', [])
        self.config['info'] = {}
        self.order = self.config['order'] = []
        self.connect('notify', config_notify_cb, self.config)

        self.names = []
        self.basic_names = []
        self.derived_names = []
        self.fields = {}

    def close(self):
        self.disconnect_by_func(config_notify_cb)

    def register_field(self, field):
        if field.name in self.names:
            raise RuntimeError("Field '{name}' already registered".format(name=field.name))
        self.names.append(field.name)
        if field.get_value:
            self.derived_names.append(field.name)
        else:
            self.basic_names.append(field.name)
        self.fields[field.name] = field

        field_config = self.config['info'].setdefault(field.name, self.old_info.get(field.name, {}))
        field.connect('notify', config_notify_cb, field_config)
        field.width = field_config.setdefault('width', field.width)
        field.visible = field_config.setdefault('visible', field.visible)
        if field.name in self.order:
            return
        if field.name not in self.old_order:
            self.order.append(field.name)
            return
        pos = self.old_order.index(field.name)
        for i, name in enumerate(self.order):
            if name not in self.old_order or self.old_order.index(name) > pos:
                self.order.insert(i, field.name)
                return
        else:
            self.order.append(field.name)

    def unregister_field(self, field):
        self.names.remove(field.name)
        if field.name in self.basic_names:
            self.basic_names.remove(field.name)
        else:
            self.derived_names.remove(field.name)
        del self.fields[field.name]
        field.disconnect_by_func(config_notify_cb)

    def song_set_fields(self, song):
        for name in self.derived_names:
            value = self.fields[name].get_value(song)
            if value is not None:
                song[name] = value

    def songs_set_fields(self, songs):
        for song in songs:
            self.song_set_fields(song)


class RowDict(GObject.Object):
    def __init__(self, data):
        super(RowDict, self).__init__()
        self.set_data(data)

    def set_data(self, data):
        GObject.Object.__setattr__(self, '_data', data)

    def get_data(self):
        return self._data

    def get_data_clean(self):
        return {key: value for key, value in self._data.items() if key[0] != '_'}

    def __getattr__(self, name):
        return self._data.get(name)

    def __setattr__(self, name, value):
        self._data[name] = value

    def __delattr__(self, name):
        self._data.pop(name, None)


class StoreBase(object):
    def __iter__(self):
        i = self.iter_children(None)
        while i:
            yield i, self.get_path(i), self.get_row(i)
            i = self.iter_next(i)

    def delete_refs(self, refs):
        for ref in refs:
            i = self.get_iter(ref.get_path())
            self.emit('song-delete', i)


class ListDictStore(StoreBase, Gtk.ListStore):
    __gsignals__ = {
        'song-new': (GObject.SIGNAL_ACTION, None, (Gtk.TreeIter,)),
        'song-delete': (GObject.SIGNAL_ACTION, None, (Gtk.TreeIter,)),
    }

    def __init__(self):
        super().__init__(RowDict)

    def get_row(self, i):
        return self.get_value(i, 0)

    def set_row(self, i, row):
        self.set_value(i, 0, RowDict(row))

    def set_rows(self, rows):
        store_set_rows(self, rows, self.set_row)


class ListDictStoreSort(StoreBase, Gtk.TreeModelSort):
    __gsignals__ = {
        'song-delete': (GObject.SIGNAL_ACTION, None, (Gtk.TreeIter,)),
    }

    def __init__(self):
        self.store = ListDictStore()
        super(ListDictStoreSort, self).__init__(self.store)

    def get_row(self, i):
        return self.store.get_row(self.convert_iter_to_child_iter(i))

    def set_rows(self, rows):
        self.store.set_rows(rows)


class AutoScrollTreeView(Gtk.TreeView):
    def __init__(self, *args, **kwargs):
        self.key_just_pressed = None

        super().__init__(*args, **kwargs)

        self.connect('key-press-event', self.key_press_event_cb)
        self.connect('destroy', lambda self: self.key_just_pressed and GLib.source_remove(self.key_just_pressed))

    @staticmethod
    def key_press_event_cb(self, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            if self.key_just_pressed:
                GLib.source_remove(self.key_just_pressed)
            self.key_just_pressed = GLib.timeout_add(200, self.key_press_event_timeout)

    def key_press_event_timeout(self):
        self.key_just_pressed = None

    def do_cursor_changed(self):
        if not self.key_just_pressed:
            return
        path, col = self.get_cursor()
        if path:
            self.scroll_to_cell(path, None, True, 0.5, 0.5)


class DictTreeView(AutoScrollTreeView):
    def __init__(self, fields, data_func, sortable):
        super().__init__(model=ListDictStoreSort() if sortable else ListDictStore(), visible=True, vexpand=True, enable_grid_lines=Gtk.TreeViewGridLines.BOTH, rubber_banding=True, search_column=0, enable_search=False)
        self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

        self.fields = fields
        self.sortable = sortable
        self.cols = {name: FieldColumn(self.fields.fields[name], data_func) for name in self.fields.order}

        self.set_search_equal_func(lambda store, col, key, i: not any(isinstance(value, str) and key.lower() in value.lower() for value in store.get_row(i).get_data().values()))

        if self.sortable:
            store = self.get_model()
            for i, name in enumerate(self.fields.order):
                self.cols[name].set_sort_column_id(i)
                store.set_sort_func(i, self.sort_func, name)

        for name in self.fields.order:
            self.append_column(self.cols[name])

        self.connect('destroy', self.destroy_cb)
        self.connect('columns-changed', self.columns_changed_cb)
        self.connect('drag-data-get', self.drag_data_get_cb)
        self.fields.connect('notify::order', self.fields_notify_order_cb)

    @staticmethod
    def destroy_cb(self):
        self.fields.disconnect_by_func(self.fields_notify_order_cb)
        self.disconnect_by_func(self.columns_changed_cb)
        del self.cols

    @staticmethod
    def sort_func(store, i, j, name):
        try:
            v1 = store.get_row(i).get_data().get(name)
            v2 = store.get_row(j).get_data().get(name)
            return 0 if v1 == v2 else -1 if v1 is None or (v2 is not None and v1 < v2) else 1
        except:
            return 0

    @staticmethod
    def columns_changed_cb(self):
        self.fields.handler_block_by_func(self.fields_notify_order_cb)
        self.fields.order = [self.get_column(i).field.name for i in range(self.get_n_columns())]
        self.fields.handler_unblock_by_func(self.fields_notify_order_cb)

    def fields_notify_order_cb(self, *args):
        self.handler_block_by_func(self.columns_changed_cb)
        last_col = None
        for name in self.fields.order:
            col = self.cols[name]
            self.move_column_after(col, last_col)
            last_col = col
        self.handler_unblock_by_func(self.columns_changed_cb)

    def get_selection_rows(self):
        store, paths = self.get_selection().get_selected_rows()
        return [store.get_row(store.get_iter(p)).get_data_clean() for p in paths], [Gtk.TreeRowReference.new(store, p) for p in paths]

    def clipboard_paste_cb(self, clipboard, raw, before):
        path, column = self.get_cursor()
        try:
            songs = ast.literal_eval(raw)
        except:
            return
        if not (isinstance(songs, list) and all(isinstance(song, dict) for song in songs)):
            return
        self.paste_at(songs, path, before)

    def paste_at(self, songs, path, before):
        selection = self.get_selection()
        selection.unselect_all()
        store = self.get_model()
        i = store.get_iter(path) if path else None
        if i and before:
            i = store.iter_previous(i)
        cursor_set = False
        for song in songs:
            if not i:
                j = store.insert(0)
            else:
                j = store.insert_after(i)
            store.set_row(j, song)
            row = Gtk.TreeRowReference.new(store, store.get_path(j))
            store.emit('song-new', j)
            i = store.get_iter(row.get_path())
            if not cursor_set:
                cursor_set = True
                self.set_cursor(store.get_path(i))
            selection.select_iter(i)

    def do_drag_begin(self, context):
        drag_songs, context.drag_refs = self.get_selection_rows()
        context.data = repr(drag_songs).encode()
        if not drag_songs:
            return
        icons = [self.create_row_drag_icon(ref.get_path()) for ref in context.drag_refs]
        width, height = icons[0].get_width(), icons[0].get_height()
        target = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height * len(context.drag_refs))
        cr = cairo.Context(target)
        cr.set_source_rgba(0, 0, 0, 1)
        cr.paint()
        y = 2
        for icon in icons:
            cr.set_source_surface(icon, 2, y)
            cr.paint()
            y += height
        icon.flush()
        Gtk.drag_set_icon_surface(context, target)

    @staticmethod
    def drag_data_get_cb(self, context, data, info, time):
        data.set(data.get_target(), 8, context.data)

    def do_drag_data_delete(self, context):
        self.get_model().delete_refs(context.drag_refs)
        context.drag_refs = []

    def do_drag_data_received(self, context, x, y, data, info, time):
        path, pos = self.get_dest_row_at_pos(x, y)
        songs = ast.literal_eval(data.get_data().decode())
        self.paste_at(songs, path, pos in [Gtk.TreeViewDropPosition.BEFORE, Gtk.TreeViewDropPosition.INTO_OR_BEFORE])

    def do_drag_end(self, context):
        del context.drag_refs

    def do_drag_motion(self, context, x, y, time):
        dest = self.get_dest_row_at_pos(x, y)
        if dest is None:
            return False
        self.set_drag_dest_row(*dest)
        if context.get_actions() & Gdk.DragAction.MOVE and not Gdk.Keymap.get_default().get_modifier_state() & Gdk.ModifierType.CONTROL_MASK:
            action = Gdk.DragAction.MOVE
        else:
            action = Gdk.DragAction.COPY
        Gdk.drag_status(context, action, time)
        return True


class TreeViewScroller(Gtk.ScrolledWindow):
    def __init__(self, treeview):
        super().__init__(visible=True)
        self.add(treeview)


class TreeViewScroller2(Gtk.Box):
    def __init__(self, treeview):
        super().__init__(visible=True, orientation=Gtk.Orientation.VERTICAL)
        treeview.set_headers_visible(False)
        headers = DictTreeView(treeview.fields, None, False)
        headers.set_vexpand(False)
        headers.set_size_request(-1, 50)
        s = TreeViewScroller(headers)
        s.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        self.pack_start(s, False, False, 0)
        self.pack_start(TreeViewScroller(treeview), True, True, 0)
        self.treeview = treeview
        treeview.bind_property('hadjustment', headers, 'hadjustment', GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)


TreeViewScroller2 = TreeViewScroller


class xScrollableTreeViewWithHeader(Gtk.Box, Gtk.Scrollable):
    hadjustment = GObject.Property(type=Gtk.Adjustment)
    hscroll_policy = GObject.Property(type=Gtk.ScrollablePolicy, default=Gtk.ScrollablePolicy.MINIMUM)
    vadjustment = GObject.Property(type=Gtk.Adjustment)
    vscroll_policy = GObject.Property(type=Gtk.ScrollablePolicy, default=Gtk.ScrollablePolicy.MINIMUM)
    reference = GObject.Property()

    def __init__(self, treeview):
        super().__init__(visible=True, orientation=Gtk.Orientation.VERTICAL)
        self.treeview = treeview
        treeview.bind_property('hadjustment', self, 'hadjustment', GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        treeview.bind_property('vadjustment', self, 'vadjustment', GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        treeview.bind_property('hscroll-policy', self, 'hscroll-policy', GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        treeview.bind_property('vscroll-policy', self, 'vscroll-policy', GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL)
        treeview.set_headers_visible(False)
        headers = DictTreeView(treeview.fields, None, False)
        self.add(treeview)
        self.add(headers)

    def do_get_border(self):
        border = Gtk.Border.new()
        border.top = 60
        return True, border

    def do_get_hadjustment(self):
        print(1)

    def do_get_vadjustment(self):
        print(2)

    def do_set_hadjustment(self, a):
        print(3, a)

    def do_set_vadjustment(self, a):
        print(4, a)

    def do_get_hscroll_policy(self):
        print(5)

    def do_get_vscroll_policy(self):
        print(6)

    def do_set_hscroll_policy(self, a):
        print(7, a)

    def do_set_vscroll_policy(self, a):
        print(8, a)


class FieldColumn(Gtk.TreeViewColumn):
    width_rw = GObject.property(type=int)

    def __init__(self, field, next_data_func):
        super(FieldColumn, self).__init__()
        self.field = field
        self.renderer = field.get_renderer()
        self.next_data_func = next_data_func
        field.bind_property('title', self, 'title', GObject.BindingFlags.SYNC_CREATE)
        field.bind_property('visible', self, 'visible', GObject.BindingFlags.SYNC_CREATE)
        self.set_min_width(field.min_width)
        self.connect('notify::width-rw', self.notify_width_rw_cb)
        field.bind_property('width', self, 'width-rw', GObject.BindingFlags.SYNC_CREATE)
        self.bind_property('width', field, 'width')
        self.set_resizable(True)
        self.set_reorderable(True)
        self.pack_start(self.renderer, True)
        self.set_cell_data_func(self.renderer, self.data_func)

    @staticmethod
    def notify_width_rw_cb(self, detail):
        if self.width_rw != self.get_width():
            self.set_fixed_width(self.width_rw)

    @staticmethod
    def data_func(self, renderer, store, i, arg):
        value = store.get_row(i).get_data().get(self.field.name)
        renderer.set_property('text', str(value) if value is not None else None)
        self.next_data_func and self.next_data_func(self, renderer, store, i, arg)
