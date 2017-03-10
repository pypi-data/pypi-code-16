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

'''Content provider'''

import os
import multiprocessing as mp
import contextlib
import functools

import feedcommas.config as config
import feedcommas.client as client
import feedcommas.cache as cache
from feedcommas.utils import get_password_cmd


@contextlib.contextmanager
def make_provider(*args, **kwargs):
    '''Context Manager for `Provider` class'''
    try:
        p = Provider(*args, **kwargs)
        yield p
    finally:
        p.stop()


def _mark_article(cached_entry, *args, **kwargs):
    read = kwargs.get('read')
    article_id = kwargs.get('id')

    if read is None or article_id is None:
        return

    for article in cached_entry.data:
        if article.id == article_id:
            article.read = read
            break


def _mark_feed(cached_entry, obj, node):
    for cached_node in cached_entry.data.bfs():
        if cached_node == node:
            cached_node.unread = node.unread
            break


class Provider:
    '''Asynchrounous content provider. Dispatches jobs of fetching data from
    commafeed to the pool of workers and calls given callbacks with fetched
    data. Also communicates with urwid loop to update it after calling a
    callback for each request.'''
    def __init__(self, urwid_loop, server_cfg):
        self.server_cfg = server_cfg
        self._error_handlers = []

        self._notify_pipe = urwid_loop.watch_pipe(lambda _: True)

        self._username = server_cfg['username']
        if server_cfg['password-cmd']:
            self._password = get_password_cmd(server_cfg['password-cmd'])
        else:
            self._password = server_cfg['password']

        self._pool = None
        self._start_pool()

    def change_credentials(self, username, password, verify=False):
        '''Changes login credentials used for HTTP Simple auth. Credentials are
        verified to be correct: Provider tries to connect with them first. If
        they're correct, they're changed and all new requests will be made using
        them.

        This function doesn't save new credentials to config, because it doesn't
        know the origin of password ('password' or 'password-cmd' option).

        This function blocks until verification is done.'''
        try:
            correct = self._call(client.login, username, password)
        except client.APIFailure:
            correct = False

        if correct is True:
            self._username = username
            self._password = password
            self._start_pool()
        return correct

    def stop(self):
        '''Stops the service: workers are forcefully terminated and
        notifications to urwid are stopped.'''
        self._pool.terminate()
        os.close(self._notify_pipe)

    def add_error_handler(self, handler):
        '''Adds error handler. All error handlers are called when any request
        returns an error. Handler should accept exception instance which caused
        an error.'''
        self._error_handlers.append(handler)

    @cache.get('articles')
    def get_articles(self, callback, *args, **kwargs):
        '''Request list of articles'''
        self._async_call(client.get_articles, callback, *args, **kwargs)

    @cache.modify([('articles', _mark_article)])
    def mark(self, callback, *args, **kwargs):
        '''Mark category or entry, depending on `type_`'''
        return self._async_call(client.mark, callback, *args, **kwargs)

    def star(self, callback, *args, **kwargs):
        '''Star an entry.'''
        return self._async_call(client.star, callback, *args, **kwargs)

    @cache.get('feeds')
    def get_feeds(self, callback):
        '''Request a tree of subscribed feeds. Returns a root feed ('All'
        feed)'''
        self._async_call(client.get_feeds, callback)

    @cache.modify([('feeds', _mark_feed)])
    def feed_updated(self, node):
        '''Well, I have to admit it. Existance of this function is a little
        hack. Generally cache is transparent, but if we don't want to implement
        some kind of database queries in cache (which maybe we'll do anyway if I
        get some free time), we need a way to tell provider that client changed
        some data which is *ONLY* displayed, but isn't sent back to
        CommaFeed.'''
        return

    def _start_pool(self):
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None

        workers_no = config.get_value(self.server_cfg, 'workers', 2, int)
        self._pool = mp.Pool(processes=workers_no,
                             initializer=client.init,
                             initargs=(self._username, self._password))

    def _async_call(self, fn, callback, *args, **kwargs):
        cb = functools.partial(self._cb, real_callback=callback)
        return self._pool.apply_async(fn, args, kwargs,
                                      callback=cb,
                                      error_callback=self._send_errors)

    def _call(self, fn, *args, **kwargs):
        return self._pool.apply(fn, args, kwargs)

    def _cb(self, data, real_callback):
        real_callback(data)
        os.write(self._notify_pipe, b'1')

    def _send_errors(self, exc):
        for handler in self._error_handlers:
            handler(str(exc))
        os.write(self._notify_pipe, b'1')
