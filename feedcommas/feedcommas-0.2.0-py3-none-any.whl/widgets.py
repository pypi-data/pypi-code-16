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

'''Custom widgets used by Feed Commas'''

import os
import functools
import collections
import webbrowser
import threading
import urwid

import feedcommas.cache as cache
from feedcommas.client import NodeData
from feedcommas.actions import handle_key
from feedcommas.config import config
from feedcommas.locale import _
from feedcommas.log import log, Level


class Progress:
    '''I couldn't resist implementing this. Displays a rotating "circle"
    indicating that some action currently takes place.'''
    def __init__(self, urwid_loop):
        self._loop = urwid_loop
        self._sync_chars = r'\|/-\|/-'
        self._char_index = 0
        self._max = 100
        self._progress = 0
        self._text = ''
        self._alarm_handle = None
        self._on_finish = None

    def setup(self, max_val, start=0, text='', on_finish=None):
        '''Setup a new progress.'''
        assert max_val > 0
        assert start >= 0
        self._char_index = 0
        self._max = max_val
        self._progress = start
        self._text = text
        self._on_finish = on_finish
        self._print()

    def update(self, add=1):
        '''Update a value of currently running progress.'''
        assert add > 0
        self._progress += add
        self._print(change_ch=False)
        if self._progress >= self._max:
            self._loop.remove_alarm(self._alarm_handle)
            log.clear()
            if self._on_finish:
                self._on_finish()

    def _print(self, change_ch=True):
        text = []
        text.append(self._sync_chars[self._char_index % len(self._sync_chars)])
        if self._text:
            text.append(self._text)
        text.append('[%d%%]' % (self._progress / self._max * 100))
        log.info(' '.join(text))

        if change_ch is True:
            self._char_index += 1
            self._alarm_handle = self._loop.event_loop.alarm(0.3, self._print)


class MenuItem(urwid.Text):
    '''Selectable and clickable menu item'''
    _selectable = True

    def __init__(self, data, selected=False):
        if selected is True:
            style = 'menu selected'
        else:
            style = 'menu item'

        markup = []

        if data.id and data.id != 'all' and data.parent.id != 'all':
            markup.append('  ' * (data.depth - 1))

        markup.append((style, data.name))

        if data.unread:
            markup.append(('metadata', '(%d)' % data.unread))

        super().__init__(markup)
        self.id = data.id

    def keypress(self, size, key):
        '''Implement keypress to handle input when this widget is focused.'''
        return key


class Menu(urwid.ListBox):
    '''Scrollable menu'''
    focus_map = {
        'menu item': 'focus menu item',
        'menu selected': 'reverse',
    }

    signals = ['selection_changed']

    def __init__(self, display):
        self._provider = display.provider

        self._root = None
        self._selected_id = 'all'
        super().__init__(urwid.SimpleFocusListWalker([]))

        self._actions = {'activate': self._selection_changed}

        self.get_feeds()

    def keypress(self, size, key):
        '''Implement keypress to handle input when this widget is focused.'''
        default = functools.partial(super().keypress, size, key)
        return handle_key(key, self._actions, self._command_map, default)

    def get_feeds(self):
        '''Fetches and updates a list of subscribed feeds and categories.'''
        self._set_feeds(NodeData('', _('Loading feed list...')))
        self._provider.get_feeds(self._set_feeds)

    def find(self, id_):
        '''Returns a NodeData with a given id.'''
        return self._root.find(id_)

    def id_data(self):
        '''Returns a list of id, name and category for each node.'''
        return [(node.id, node.name, node.is_category)
                for node in self._root.dfs() if node.id]

    def handle_read(self, article_id, feed_id, read):
        '''`mark_read` signal handler. Updates a number of unread articles.'''
        node = self.find(feed_id)
        if node is None:
            return

        if node.unread is not None:
            if read is True:
                node.unread -= 1
            else:
                node.unread += 1
        self.refresh()
        self._provider.feed_updated(node)

    def refresh(self):
        '''Refreshes a list of feeds.'''
        self._set_feeds(self._root)

    def _selection_changed(self):
        widget, _ = self.get_focus()
        data = self.find(widget.original_widget.id)

        if data.id and self._selected_id != data.id:
            self._selected_id = data.id
            self.refresh()
            urwid.emit_signal(self, 'selection_changed',
                              data.id, data.is_category)

    def _set_feeds(self, node_data):
        _, pos = self.get_focus()

        self.body.clear()  # pylint: disable=no-member
        self._root = node_data
        node_data.dfs()
        for node in node_data.dfs():
            selected = (node.id == self._selected_id)
            w = urwid.AttrMap(MenuItem(node, selected), None, self.focus_map)
            self.body.append(w)  # pylint: disable=no-member

        # This keeps focus (not selection) on the same position, not the same
        # node. It's less astonishing than a 'focus jump' to the other part of
        # feed list.
        if pos and pos < len(self.body):
            self.set_focus(pos)


class Article(urwid.Pile):
    '''Text area with customized markup for displaying articles.'''
    _selectable = False

    def __init__(self, article):
        self.data = article
        super().__init__(self._markup())
        self.focus_item = self[-2]  # focus body

    def keypress(self, size, keys):
        '''Implement keypress to handle input when this widget is focused.'''
        return keys

    def update(self):
        '''Re-draws article contents (header, body and a footer).'''
        self.contents.clear()
        for widget in self._markup():
            self.contents.append((widget, ('weight', 1)))
        self.focus_item = self[-2]  # focus body

    @staticmethod
    def _make_header(article):
        title = urwid.Text([('title', article.title)])
        date = urwid.Text([('metadata', article.date)], align='right')
        return [('weight', 10, title), ('weight', 3, date)]

    @staticmethod
    def _make_footer(article):
        status = ''
        if article.starred:
            status += '\u2605'  # unicode BLACK STAR

        # unicode BALLOT BOX and BALLOT BOX WITH CHECK
        status += '\u2611' if article.read else '\u2610'

        status_widget = urwid.Text([('metadata', status)])

        source_markup = []
        if article.author:
            source_markup.append(('metadata', '%s, ' % article.author))
        source_markup.append(('metadata', article.feed_name))

        source_widget = urwid.Text(source_markup, align='right')

        return [('weight', 1, status_widget), ('weight', 10, source_widget)]

    def _markup(self):
        header = urwid.Columns(self._make_header(self.data))
        body = urwid.Text([('article', self.data.content)])
        footer = urwid.Columns(self._make_footer(self.data))
        body._selectable = True  # pylint: disable=protected-access
        return [header, urwid.Divider(), body, footer]


class Indicator(urwid.Text):
    '''Indicator displayed on an article list telling that "something" is
    happening right now.'''
    def __init__(self, text):
        markup = [('metadata', text)]
        super().__init__(markup, align='center')


class ArticleList(urwid.ListBox):
    '''Scrollable list of articles'''
    _focus_map = {
        None: 'focus line',  # hacky, but works. :)
        'title': 'focus title',
        'article': 'focus article',
    }

    _GetType = collections.namedtuple('GetType', ('type_', 'id'))

    signals = ['mark_read']

    def __init__(self, display):
        self._provider = display.provider
        self._loop = display.urwid_loop

        self.walker = urwid.SimpleFocusListWalker([])
        super().__init__(self.walker)

        self._actions = {
            'open-browser': self._open_browser,
            'toggle-read': self._toggle_read_current,
            'toggle-star': self._toggle_star_current,
        }

        display.cmd_handler.register_actions(self._actions, self)

        self._limit = 20
        self._maybe_more = False
        self._indicators_count = 0

        # NOTE: filter() manages some class attributes (_filter and _show_read)
        self.filter('all', is_category=True,
                    read=config()['settings'].getboolean('show-read'),
                    ind=_('Loading articles...'))

    def keypress(self, size, key):
        '''Implement keypress to handle input when this widget is focused.'''
        name = self._command_map[key]
        if name and name.startswith('cursor '):
            return self._navigate(size, key)

        default = functools.partial(super().keypress, size, key)
        return handle_key(key, self._actions, self._command_map, default)

    @property
    def focus_percentage(self):
        '''Return position of currently focused article, expressed in
        percents.'''
        try:
            return int(100 * self.focus_position / self.count)
        except ZeroDivisionError:
            return 0

    @property
    def limit(self):
        '''Returns a per-page limit of downloaded articles.'''
        return self._limit

    def filter(self, id_=None, is_category=None, read=None, ind=None):
        '''Displays only articles from a feed or category (`is_category`
        argument decides) with a matching id.'''
        if id_ is not None and is_category is not None:
            if is_category:
                self._filter = self._GetType('category', id_)
            else:
                self._filter = self._GetType('feed', id_)
        if read is not None:
            self._show_read = read

        if ind is not None:
            self.clear()
            self._indicate(ind)

        self._get_articles(self._set_articles)

    def configure_read(self, show_read):
        '''Switch to all/only unread view. Updates configuration accordingly.'''
        self.filter(read=show_read)
        config()['settings']['show-read'] = str(show_read)

    @property
    def current(self):
        '''Unwraps Article widget and returns it.'''
        try:
            return self._unwrap_article(self.focus)
        except AttributeError:
            return None

    @property
    def count(self):
        '''Returns number of displayed articles'''
        return len(self.walker) - self._indicators_count

    def clear(self):
        '''Clears all contents of ArticleList.'''
        self.walker.clear()
        self._indicators_count = 0

    def _navigate(self, size, key):
        if self._maybe_more and self.focus_percentage > 75:
            self._maybe_more = False  # don't add multiple "Loading..." labels
            self._indicate(_('Loading next articles...'))
            self._get_articles(self._add_articles, offset=self.count)

        ret = super().keypress(size, key)

        # after position change, automatically mark a new article as read after
        # a few seconds, but only if it's still focused after that time.
        if self.current and self.current.data.read is False:
            tm = int(config()['settings']['mark-read-time'])
            if tm >= 0:
                cb = functools.partial(self._auto_read, self.focus_position)
                self._loop.event_loop.alarm(tm, cb)

        return ret

    def _unwrap_article(self, widget):
        try:
            while not isinstance(widget, Article):
                widget = widget.original_widget
        except AttributeError:
            return None
        return widget

    def _get_articles(self, cb, **kwargs):
        if self._show_read is True:
            read_type = 'all'
        else:
            read_type = 'unread'
        self._provider.get_articles(cb, self._filter.type_, id=self._filter.id,
                                    limit=self.limit, readType=read_type,
                                    **kwargs)

    def _set_articles(self, articles):
        self.clear()
        self._add_articles(articles)
        self._maybe_more = bool(len(articles) == self.limit)
        if self.count > 0:
            self.focus_position = 0
        else:
            self._indicate(_('No articles'))

    def _add_articles(self, articles):
        self._remove_indicators()
        self._maybe_more = bool(len(articles) == self.limit)
        for article in articles:
            text = urwid.LineBox(Article(article))
            self.walker.append(urwid.AttrMap(text, None, self._focus_map))

    def _toggle_star_current(self):
        pos = self.focus_position
        try:
            data = self.current.data
        except (IndexError, AttributeError):
            return
        self._star(pos, not data.starred)

    def _toggle_read_current(self):
        pos = self.focus_position
        try:
            data = self.current.data
        except (IndexError, AttributeError):
            return
        self._read(pos, not data.read)

    def _auto_read(self, pos):
        if pos == self.focus_position:
            self._read(pos, True)

    def _read(self, pos, read):
        try:
            article = self._unwrap_article(self.walker[pos])
            data = article.data
        except (IndexError, AttributeError):
            return
        if data.markable and data.read != read:
            data.read = read
            urwid.emit_signal(self, 'mark_read', data.id, data.feed_id, read)
            self._provider.mark(lambda _: True, 'entry', id=data.id, read=read)
            article.update()

    def _star(self, pos, star):
        try:
            article = self._unwrap_article(self.walker[pos])
            data = article.data
        except (IndexError, AttributeError):
            return
        if data.starred != star:
            data.starred = star
            self._provider.star(lambda _: True,
                                id=data.id, feedId=data.feed_id, starred=star)
            article.update()

    def _remove_indicators(self):
        for i, elem in enumerate(self.walker):
            if isinstance(elem, Indicator):
                del self.walker[i]

    def _indicate(self, text):
        self.walker.append(Indicator(text))
        self._indicators_count += 1

    def _open_browser(self):
        if not self.current:
            return

        # Browsers like to print. we don't like prints because they appear in
        # the middle of gui. Suppress the prints!
        savout = os.dup(1)
        saverr = os.dup(2)
        os.close(1)
        os.close(2)

        os.open(os.devnull, os.O_RDWR)
        try:
            # new=2: try opening in a new tab
            webbrowser.open(self.current.data.url, new=2)
            self._read(self.focus_position, True)
        finally:
            os.dup2(savout, 1)
            os.dup2(saverr, 2)


class Commandline(urwid.Pile):
    '''Bottom command line activated by pressing a colon key.'''
    signals = ['command', 'command_cancel']
    _selectable = True

    def __init__(self, abbrev_getter, *args, **kwargs):
        self._e = urwid.Edit(multiline=True)
        super().__init__([self._e])
        self._abbrev = abbrev_getter
        self._compl_index = None
        self._uncompl_cmd = ''

    def set_caption(self, markup):
        '''Forward `set_caption` to the underlying urwid.Edit'''
        self._e.set_caption(markup)

    def keypress(self, size, key):
        '''Implement keypress to handle input when this widget is focused.'''
        self._e.set_caption('')
        if key == 'enter':  # hardcoded by design
            urwid.emit_signal(self, 'command', self._e.edit_text[1:])
            self._e.set_edit_text('')
            self._edited()
        elif key == 'tab':
            self._complete()
        elif key == 'backspace' and self._e.edit_text == ':':
            self._e.set_edit_text('')
            urwid.emit_signal(self, 'command_cancel')
            self._edited()
        elif key == 'esc':
            self._e.set_edit_text('')
            urwid.emit_signal(self, 'command_cancel')
            self._edited()
        else:
            ret = super().keypress(size, key)
            self._edited()
            return ret

    def _edited(self):
        self._hide_abbrev()
        self._compl_index = 0
        self._uncompl_cmd = self._e.edit_text[1:]

    def _complete(self):
        completions = self._abbrev(self._uncompl_cmd)
        completions.sort()
        if len(completions) == 0:
            return

        if self._compl_index >= len(completions):
            self._compl_index = 0

        self._e.set_edit_text(':%s' % completions[self._compl_index])
        self._e.set_edit_pos(len(self._e.edit_text))
        self._show_abbrev(completions)
        self._compl_index += 1

    def _show_abbrev(self, abbr_list):
        if len(abbr_list) < 2:
            return

        markup = []
        for i, abbr in enumerate(abbr_list):
            if i == self._compl_index:
                markup.append(('reverse', abbr))
            else:
                markup.append(abbr)
            markup.append('  ')
        markup.pop()

        if len(self.contents) > 1:
            self.contents[0][0].set_text(markup)
        else:
            txt = urwid.Text(markup)
            self.contents.insert(0, (txt, ('weight', 1)))

    def _hide_abbrev(self):
        while len(self.contents) > 1:
            self.contents.pop(0)


class Display(urwid.Columns):
    '''Main two-column display'''
    _Handler = collections.namedtuple('Handler', ('obj', 'fn'))

    def __init__(self, provider, urwid_loop, cmd_handler):
        self.provider = provider
        self.urwid_loop = urwid_loop
        self.cmd_handler = cmd_handler

        self._articles = ArticleList(self)
        self._menu = Menu(self)
        vline = urwid.AttrMap(urwid.SolidFill(u'\u2502'), 'menu line')
        super().__init__([('weight', 2, self._menu),
                          ('fixed', 1, vline),
                          ('weight', 7, self._articles)])

        self.focus_position = 2

        self._sync_lock = threading.Lock()
        self._sync_wait = None
        self._sync_ready = None

        self._actions = {
            'show-all': lambda: self._articles.configure_read(True),
            'show-unread': lambda: self._articles.configure_read(False),
            'refresh': self._refresh,
            'sync': self._sync
        }

        self.cmd_handler.register_actions(self._actions, self)

        urwid.connect_signal(self._menu, 'selection_changed',
                             self._articles.filter)
        urwid.connect_signal(self._articles, 'mark_read',
                             self._menu.handle_read)

    def keypress(self, size, key):
        '''Implement keypress to handle input when this widget is focused.'''
        default = functools.partial(super().keypress, size, key)
        return handle_key(key, self._actions, self._command_map, default)

    def _refresh(self):
        cache.clear()
        self._articles.filter(ind=_('Refreshing...'))
        self._menu.get_feeds()

    def _sync(self):
        '''Hacky way to synchronize. Simply caches all feeds and categories,
        both read and unread, with limit the same as in ArticleList.'''
        if cache.cache_time() <= 0:
            log.error(_('To synchronize feeds for offline reading '
                        'set settings.cache-time.'))
            return

        if not self._sync_lock.acquire(blocking=False):
            log.error(_('Synchronization already in progress.'))
            return

        id_data = self._menu.id_data()

        def _on_finish():
            self._sync_lock.release()

        progress = Progress(self.urwid_loop)
        progress.setup(len(id_data) * 2, text=_('Synchronization'),
                       on_finish=_on_finish)

        def _cb(*args):
            progress.update()

        cache.clear()
        self._menu.get_feeds()
        for id_, __, category in id_data:
            type_ = 'category' if category else 'feed'
            self.provider.get_articles(_cb, type_, id=id_, readType='all',
                                       limit=self._articles.limit)
            self.provider.get_articles(_cb, type_, id=id_, readType='unread',
                                       limit=self._articles.limit)


class MainWindow(urwid.Frame):
    '''Urwid top widget.'''
    def __init__(self, provider, urwid_loop, cmd_handler):
        self.commandline = Commandline(cmd_handler.get_abbrev_names)
        urwid.connect_signal(log, 'log', self.log)
        urwid.connect_signal(log, 'clear', self.log_clear)

        self.display = Display(provider, urwid_loop, cmd_handler)
        super().__init__(self.display, footer=self.commandline)

        urwid.connect_signal(self.commandline, 'command',
                             self._command_finished)
        urwid.connect_signal(self.commandline, 'command',
                             cmd_handler.call)
        urwid.connect_signal(self.commandline, 'command_cancel',
                             self._command_finished)

        provider.add_error_handler(functools.partial(self.log, Level.error))

    def keypress(self, size, key):
        if key == ':':  # hardcoded by design
            self.focus_position = 'footer'
        return super().keypress(size, key)

    def log(self, level, text):
        '''Common, reliable way of displaying log prints.'''
        if level == Level.error:
            style = 'error'
        else:
            style = 'log'
        self.commandline.set_caption([(style, text)])

    def log_clear(self):
        '''Clear current print.'''
        self.commandline.set_caption('')

    def _command_finished(self, *args, **kwargs):
        self.focus_position = 'body'
