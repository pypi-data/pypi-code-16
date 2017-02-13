"""
tmpld.core.tags
~~~~~~~~~~~~~~

Jinja2 Tags for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os

import jinja2
import jinja2.ext


class EmbedTag(jinja2.ext.Extension):
    """
    This will give us an {% embed '/path/to/file' %} tag.
    """

    tags = set(['embed'])

    def _build_path(self, dir_name, embed_path):
        if embed_path.startswith(('/', '~')):
            full_path = os.path.expanduser(embed_path)
        else:
            full_path = os.path.join(dir_name, embed_path)
        return os.path.realpath(full_path)

    def _get_contents(self, path, default, strip, strip_comments):
        try:
            with open(path, 'rt') as fd:
                contents = fd.read()
        except FileNotFoundError:
            contents = default or ''
        if strip_comments:
            contents = '\n'.join(
                [l for l in contents.split('\n') if not l.startswith('#')]
            )
        if strip:
            contents = contents.strip()
        return contents

    def _parse_tokens(self, parser):
        dir_name = os.path.dirname(parser.filename)
        next(parser.stream)  # skip the tag name
        embed_path = parser.parse_expression().value

        parser.stream.skip_if('comma')
        default = parser.stream.next_if('string')
        if default:
            default = default.value

        parser.stream.skip_if('comma')
        if parser.stream.skip_if('name:strip'):
            parser.stream.skip(1)
            strip = parser.parse_expression().value
        else:
            strip = True

        parser.stream.skip_if('comma')
        if parser.stream.skip_if('name:strip_comments'):
            parser.stream.skip(1)
            strip_comments = parser.parse_expression().value
        else:
            strip_comments = False

        path = self._build_path(dir_name, embed_path)
        return path, default, strip, strip_comments

    def parse(self, parser):
        contents = self._get_contents(*self._parse_tokens(parser))
        node = jinja2.nodes.TemplateData(contents)
        return jinja2.nodes.Output([node])
