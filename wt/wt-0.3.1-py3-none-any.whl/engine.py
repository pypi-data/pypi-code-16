# -*- coding: utf-8 -*-

import os
import datetime
import itertools
import logging
import urllib.parse
from collections import OrderedDict
from pathlib import Path
from shutil import copytree, rmtree

import yaml
from cached_property import cached_property

from .base import Config, Page, Post
from .jinja import get_env
from .exceptions import UrlNotFoundError, InvalidLocalLinkError
from .paginator import Paginator
from .parser import HTMLParser


class WT(object):

    def __init__(self, filename, is_prod=False):
        self.config_filename = filename
        self.workdir = os.path.dirname(filename)
        self.logger = logging.getLogger('wt.blog')
        self.is_prod = is_prod

        conf = None
        if os.path.isfile(filename):
            with open(filename, encoding='utf-8') as f:
                try:
                    conf = yaml.load(f)
                    assert isinstance(conf, dict)
                except (yaml.YAMLError, AssertionError):
                    conf = {}
                    self.logger.error('Error parsing yaml', exc_info=True)
        else:
            self.logger.warn('Missing config file "%s"', filename)

        self.conf = Config(conf or {})

    @cached_property
    def static_root(self):
        static_root = self.conf.path('directories.static', 'static')
        return os.path.join(self.workdir, static_root)

    @cached_property
    def with_feed(self):
        return self.conf.path('build.feed', True)

    @cached_property
    def verify_links(self):
        return self.conf.path('verify.links', False)

    @cached_property
    def pages(self):
        pages = self.conf.pages or []
        return {x['url']: Page.from_dict(self.workdir, x) for x in pages}

    @cached_property
    def posts(self):
        posts = self.conf.posts or []
        posts.sort(key=lambda x: x['modified'], reverse=True)
        dst = OrderedDict()
        _prev = None
        for idx, post in enumerate(posts):
            p = Post.from_dict(self.workdir, post)
            if idx > 0:
                p.next = _prev
                _prev.prev = p
            dst[p['url']] = _prev = p
        return dst

    def paginator(self, path='/'):
        return Paginator(
            list(self.posts.values()), path, **self.conf.path('paginate', {}))

    @cached_property
    def env(self):
        return get_env(self.workdir, **self.conf.path('jinja', {}))

    @cached_property
    def parser(self):
        return HTMLParser()

    @cached_property
    def local_links(self):
        links = list(
            itertools.chain(
                ['/'] if '/' not in self.pages else [],
                ['/atom.xml'] if self.with_feed else [],
                (x for x in self.paginator().pages.keys() if x != '/'),
                self.pages.keys(),
                self.posts.keys(),
            ))
        return links

    def render_html(self, template, **context):
        tmpl = self.env.get_template(template)
        html = tmpl.render(**context)
        if self.verify_links:
            html = self.do_verify_links(html)
        return html

    def render(self, path, headers=None):
        headers = headers or {}
        host = headers.get('Host')
        now = datetime.datetime.utcnow()
        if path.endswith('atom.xml') and self.with_feed:
            tmpl = self.conf.path('templates.feed', 'atom.xml')
            return self.render_html(tmpl,
                                    wt=self,
                                    config=self.conf,
                                    host=host,
                                    now=now,
                                    is_prod=self.is_prod,
                                    posts=self.posts.values(),
                                    pages=self.pages.values())
        elif path in self.pages:
            page = self.pages[path]
            tmpl = (
                page.template or self.conf.path('templates.page', 'page.html'))
            return self.render_html(tmpl,
                                    wt=self,
                                    now=now,
                                    is_prod=self.is_prod,
                                    content=page,
                                    config=self.conf)
        elif path in self.posts:
            post = self.posts[path]
            tmpl = (
                post.template or self.conf.path('templates.post', 'post.html'))
            return self.render_html(tmpl,
                                    wt=self,
                                    now=now,
                                    is_prod=self.is_prod,
                                    content=post,
                                    config=self.conf)

        tmpl = self.conf.path('templates.mainpage', 'mainpage.html')
        posts = list(self.posts.values())
        paginator = self.paginator(path)
        if path == '/' or path in paginator.pages:
            return self.render_html(tmpl,
                                    wt=self,
                                    config=self.conf,
                                    paginator=paginator,
                                    posts=posts,
                                    pages=self.pages,
                                    is_prod=self.is_prod,
                                    host=host,
                                    now=now)

        raise UrlNotFoundError

    @cached_property
    def output_path(self):
        output = Path(self.conf.path('build.output', 'output'))
        if not output.is_absolute():
            output = Path(self.workdir).joinpath(output)
        return output.expanduser()

    def build(self):
        build_static = bool(self.conf.path('build.static', False))
        output = self.output_path
        self.logger.info('Building pages to %s directory', str(output))
        if output.exists():
            self.logger.info('  * output directory exists, cleaning')
            rmtree(str(output))
        if build_static:
            self.logger.info('  + copying static files')
            copytree(self.static_root, str(output))
        else:
            output.mkdir(parents=True)
        for path in self.local_links:
            self.logger.info('  + building path "%s"', path)
            html = self.render(path)
            if path.endswith('/'):
                path += 'index.html'
            target = output.joinpath(path.lstrip('/'))
            parent = target.parent
            parent.mkdir(parents=True, exist_ok=True)
            target.write_text(html, encoding='utf-8')
        self.logger.info('done')

    def do_verify_links(self, html):

        links = self.parser.get_links(html)

        def is_local(parsed_link):
            return parsed_link.scheme == '' and parsed_link.netloc == ''

        for link in links:
            parsed = urllib.parse.urlparse(link)
            if is_local(parsed) and \
               parsed.path not in self.local_links and \
               not self.is_valid_static_link(parsed.path):
                # FIXME show line numbers?
                # this is generated html so line numbers might not be useful
                self.logger.warning('[!] Bad local link "%s" found', link)
                if self.is_prod:
                    raise InvalidLocalLinkError
        return html

    def is_valid_static_link(self, link):
        return os.path.exists(os.path.join(self.static_root, link.lstrip('/')))
