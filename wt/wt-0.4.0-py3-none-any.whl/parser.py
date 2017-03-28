# -*- coding: utf-8 -*-

from collections import defaultdict
from html.parser import HTMLParser as BaseHTMLParser


class HTMLParser(BaseHTMLParser):
    link_attrs = ('src', 'href')
    skip_content_for_tags = ('code', )

    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.reset()

    def reset(self):
        self.links_pos = defaultdict(list)
        self.skipping_content = False
        super().reset()

    def handle_starttag(self, tag, attrs):

        if self.skipping_content:
            return

        for name, value in attrs:
            if name in self.link_attrs:
                pos = self.getpos()
                self.links_pos[value].append(pos)

        if tag in self.skip_content_for_tags:
            self.skipping_content = True

    def handle_endtag(self, tag):
        if tag in self.skip_content_for_tags:
            self.skipping_content = False

    def get_links(self, html):
        self.reset()
        self.feed(html)
        return self.links_pos.copy()
