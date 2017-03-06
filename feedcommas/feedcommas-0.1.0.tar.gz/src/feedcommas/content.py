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
import sys
import subprocess
import multiprocessing as mp
import contextlib
import functools

import feedcommas.config as config
import feedcommas.client as client
import feedcommas.cache as cache


@contextlib.contextmanager
def make_provider(*args, **kwargs):
    '''Context Manager for `Provider` class'''
    try:
        p = Provider(*args, **kwargs)
        yield p
    finally:
        p.stop()


class Provider:
    '''Asynchrounous content provider. Dispatches jobs of fetching data from
    commafeed to the pool of workers and calls given callbacks with fetched
    data. Also communicates with urwid loop to update it after calling a
    callback for each request.'''
    def __init__(self, urwid_loop, server_cfg):
        self._error_handlers = []

        self._password = None
        if server_cfg['password-cmd']:
            enc = sys.stdout.encoding
            cmd = server_cfg['password-cmd']
            self._password = subprocess.check_output(cmd, shell=True).decode(enc)
            self._password = self._password.rstrip('\r\n')

        workers_no = config.get_value(server_cfg, 'workers', 2, int)
        self._pool = mp.Pool(processes=workers_no,
                             initializer=client.init,
                             initargs=(self._password,))
        self._notify_pipe = urwid_loop.watch_pipe(lambda _: True)

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

    @cache.invalidate('feeds')
    def mark(self, callback, *args, **kwargs):
        '''Mark category or entry, depending on `type_`'''
        self._async_call(client.mark, callback, *args, **kwargs)

    def star(self, callback, *args, **kwargs):
        '''Star an entry.'''
        self._async_call(client.star, callback, *args, **kwargs)

    @cache.get('feeds')
    def get_feeds(self, callback):
        '''Request a tree of subscribed feeds. Returns a root feed ('All'
        feed)'''
        self._async_call(client.get_feeds, callback)

    def _async_call(self, fn, callback, *args, **kwargs):
        cb = functools.partial(self._cb, real_callback=callback)
        self._pool.apply_async(fn, args, kwargs,
                               callback=cb,
                               error_callback=self._send_errors)

    def _cb(self, data, real_callback):
        real_callback(data)
        os.write(self._notify_pipe, b'1')

    def _send_errors(self, exc):
        for handler in self._error_handlers:
            handler(str(exc))
        os.write(self._notify_pipe, b'1')
