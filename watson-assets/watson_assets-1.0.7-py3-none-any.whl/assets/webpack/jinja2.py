# -*- coding: utf-8 -*-
import json
from jinja2.ext import Extension
from jinja2 import nodes
from watson.assets.webpack import exceptions
from watson.common.decorators import cached_property


__all__ = ['webpack']


class WebpackExtension(Extension):
    tags = set(['webpack'])
    cached_stats = None

    @cached_property
    def config(self):
        conf = self.environment.application.config
        return conf.get('assets', {}).get('webpack', {})

    def parse(self, parser):
        stream = parser.stream
        lineno = next(stream).lineno
        bundle = nodes.Const('main')
        type_ = nodes.Const(None)
        first = True
        kwargs = []
        while stream.current.type != 'block_end':
            if not first:
                stream.expect('comma')
            first = False
            if stream.current.test('name') and stream.look().test('assign'):
                name = next(stream).value
                stream.skip()
                value = parser.parse_expression()
                if name == 'bundle':
                    bundle = value
                elif name == 'type':
                    type_ = value
                else:
                    kwargs.append(nodes.Keyword(name, value))
        args = [bundle, type_]
        call = self.call_method('render', args=args, kwargs=kwargs)
        call_block = nodes.CallBlock(call, [], [], [])
        call_block.set_lineno(lineno)
        return call_block

    def load_stats(self):
        if self.config.get('use_cache', True) and self.cached_stats:
            return
        data = {
            'chunks': {
                'main': []
            }
        }
        try:
            with open(self.config.get('stats_file', 'webpack-stats.json')) as f:
                data = json.load(f)
        except:
            raise exceptions.NotReadyError('Stats file not found, run Webpack.')
        self.cached_stats = data

    def _render(self, asset, type_=None):
        extension = asset.split('.')[-1]
        if extension == type_ or not type_:
            asset_path = '{}/{}'.format(
                self.config.get('bundle_dir', ''), asset)
            return self._render_tag(asset_path)

    def _render_tag(self, asset):
        if asset.endswith('.js'):
            return '<script type="text/javascript" src="{}"></script>'.format(
                asset)
        elif asset.endswith('.css'):
            return '<link type="text/css" href="{}" rel="stylesheet">'.format(
                asset)

    def render(self, bundle, type_, caller=None, **kwargs):
        self.load_stats()
        if self.cached_stats['status'] != 'done':
            raise exceptions.NotReadyError(
                'Invalid stats file, please run Webpack again.')
        assets = []
        for _bundle in self.cached_stats['chunks'].get(bundle, []):
            asset = self._render(_bundle['name'], type_)
            if asset:
                assets.append(asset)
        return '\n'.join(assets)

webpack = WebpackExtension
