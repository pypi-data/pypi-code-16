# -*- coding: utf-8 -*-

import logging

from collections import OrderedDict

from cached_property import cached_property

from .exceptions import BadPaginatorUrlError, BadPaginatorPageError


class Paginator(object):

    def __init__(self, object_list, path, mainpage=True, **kwargs):
        self.page_size = kwargs.get('page_size') or kwargs.get('by')
        self.orphans = kwargs.get('orphans')
        self.mainpage = bool(mainpage)
        self.object_list = object_list
        self.path = path

        self.logger = logging.getLogger('wt.paginator')

        url = kwargs.get('url', '/page{page_number}.html')
        if not url.startswith('/'):
            raise BadPaginatorUrlError(
                'Bad paginator url pattern "%s" in config '
                '(must be an absolute path starting with "/")' % url)
        if '{page_number}' not in url:
            msg = ('Bad paginator url pattern "%s" in config '
                   '(it must have "{page_number}" placeholder)')
            raise BadPaginatorUrlError(msg % url)
        if not url.endswith('.html') and url[-1] != '/':
            msg = ('Bad paginator url pattern "%s" in config '
                   '(not a directory and doesn\'t have .html extension)')
            raise BadPaginatorUrlError(msg % url)
        self.url = url

    @cached_property
    def num_pages(self):
        if not self.page_size or self.page_size < 1:
            return 1
        cnt = len(self.object_list)
        num_pages, rem = divmod(cnt, self.page_size)
        if rem > 0:
            if (self.orphans and rem > self.orphans) or not self.orphans:
                num_pages += 1
        return num_pages

    @cached_property
    def pages(self):
        return OrderedDict(self._pages())

    @cached_property
    def page_num(self):
        if self.path in self.pages:
            return self.pages[self.path]
        msg = 'Unknown page for path "%s"'
        self.logger.error(msg, self.path)
        raise BadPaginatorPageError(msg % self.path)

    @cached_property
    def items(self):
        if not self.page_size or self.page_size < 1:
            return self.object_list
        page_num, orphans = self.page_num, self.orphans
        num_items = len(self.object_list)
        first = (page_num - 1) * self.page_size
        last = first + self.page_size
        if orphans and last < num_items and last + orphans >= num_items:
            last += orphans
        return self.object_list[first:last]

    @cached_property
    def has_next(self):
        return self._next_url in self.pages

    @cached_property
    def has_prev(self):
        return self._prev_url in self.pages

    @cached_property
    def next_page(self):
        url = self._next_url
        return url, self.pages.get(url)

    @cached_property
    def prev_page(self):
        url = self._prev_url
        return url, self.pages.get(url)

    @cached_property
    def first_page(self):
        k = list(self.pages.keys())[0]
        return k, self.pages[k]

    @cached_property
    def last_page(self):
        k = list(self.pages.keys())[-1]
        return k, self.pages[k]

    def _pages(self):
        first = 1
        if self.mainpage:
            yield '/', 1
            first += 1
        for x in range(first, self.num_pages + 1):
            yield self.url.format(page_number=x), x

    @cached_property
    def _next_url(self):
        page_num = self.page_num
        return self.url.format(page_number=page_num + 1)

    @cached_property
    def _prev_url(self):
        page_num = self.page_num - 1
        if self.mainpage and page_num == 1:
            return '/'
        return self.url.format(page_number=page_num)
