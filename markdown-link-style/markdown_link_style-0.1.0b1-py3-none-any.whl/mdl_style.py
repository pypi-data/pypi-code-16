# -*- coding: utf-8 -*-
#
#   Copyright © 2017 markdown-link-style contributors.
#
#    This file is part of markdown-link-style.
#
#   markdown-link-style is free software: you can redistribute it
#   and/or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   markdown-link-style is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#   See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with markdown-link-style (see COPYING).  If not, see
#   <http://www.gnu.org/licenses/>.

import argparse
import re

from mistune import (BlockGrammar, BlockLexer, InlineLexer, Renderer,
                     Markdown)

from markdown_link_style.logging import MDLSLogger
from markdown_link_style._version import __version__


# Initialize logger for this module.
logger = MDLSLogger(__name__)


# from mistune
_inline_tags = [
    'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr', 'data',
    'time', 'code', 'var', 'samp', 'kbd', 'sub', 'sup', 'i', 'b', 'u', 'mark',
    'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'br', 'wbr', 'ins', 'del',
    'img', 'font',
]
_valid_end = r'(?!:/|[^\w\s@]*@)\b'
_block_tag = r'(?!(?:%s)\b)\w+%s' % ('|'.join(_inline_tags), _valid_end)


def _pure_pattern(regex):
    """Function from mistune."""
    pattern = regex.pattern
    if pattern.startswith('^'):
        pattern = pattern[1:]
    return pattern


class LSBlockGrammar(BlockGrammar):

    def __init__(self):
        # remove list_block and block_quote from paragraph
        self.paragraph = re.compile(
            r'^((?:[^\n]+\n?(?!'
            r'%s|%s|%s|%s|%s|%s|%s'
            r'))+)\n*' % (
                _pure_pattern(self.fences).replace(r'\1', r'\2'),
                _pure_pattern(self.hrule),
                _pure_pattern(self.heading),
                _pure_pattern(self.lheading),
                _pure_pattern(self.def_links),
                _pure_pattern(self.def_footnotes),
                '<' + _block_tag,
            )
        )


class LSBlockLexer(BlockLexer):
    """Link Style Block Lexer.

    """
    grammar_class = LSBlockGrammar

    def __init__(self, rules=None, **kwargs):
        super(LSBlockLexer, self).__init__(rules, **kwargs)

        # Only parse these block rules.
        self.default_rules = ['def_links', 'paragraph', 'text']


class LSInlineLexer(InlineLexer):
    """Link Style Inline Lexer.

    """

    def __init__(self, renderer, rules=None, **kwargs):
        super(LSInlineLexer, self).__init__(renderer, rules, **kwargs)

        # Only parse these inline rules
        self.default_rules = ['autolink', 'link', 'reflink', 'text']


class LSRenderer(Renderer):
    """Link Style Renderer.

    """

    def __init__(self, **kwargs):
        super(LSRenderer, self).__init__(**kwargs)

        # Link style is either 'inline' or 'footnote'.
        self.link_style = self.options.get('link_style')

        self.fn_lnk_num = 0 # footnote style link number
        self.fn_lnk_refs = [] # footnote style link refs

    def text(self, text):
        return text

    def autolink(self, link, is_email=False):
        return '<{}>'.format(link)

    def paragraph(self, text):
        p = text
        fn_refs = self._pop_fn_refs()

        if fn_refs:
            # Insert footnote refs, if any, after paragraph.
            return '\n{}\n\n{}'.format(p, fn_refs)

        return '\n{}\n'.format(p)

    def link(self, link, title, text):
        link_text = self._stylize_link(link, title, text)
        return link_text

    def image(self, src, title, text):
        # Markup for images are same as links, except it is prefixed
        # with a bang (!).
        return '{}{}'.format('!', self.link(src, title, text))

    def _stylize_link(self, link, title, text):
        if self.link_style == 'inline':
            return self._gen_inline_link(link, title, text)
        else:
            return self._gen_footnote_link(link, title, text)

    def _gen_inline_link(self, link, title, text):
        if title:
            return '[{}]({} "{}")'.format(text, link, title)
        else:
            return '[{}]({})'.format(text, link)

    def _gen_footnote_link(self, link, title, text):
        fn_num = self._st_fn_ref(link, title)
        return '[{}][{}]'.format(text, fn_num)

    def _st_fn_ref(self, link, title):
        """Store footnote link reference.

        """
        fn_num = self._get_fn_lnk_num()

        if title:
            fn_ref = '[{}]: {} ({})'.format(fn_num, link, title)
        else:
            fn_ref = '[{}]: {}'.format(fn_num, link)

        self.fn_lnk_refs.append(fn_ref)
        return fn_num

    def _get_fn_lnk_num(self):
        """Get footnote link number.

        """
        fn_num = self.fn_lnk_num
        self.fn_lnk_num = self.fn_lnk_num + 1
        return fn_num

    def _pop_fn_refs(self):
        """Pop all footnote refs and return them as a string.

        """
        refs = ''

        for ref in self.fn_lnk_refs:
            refs += '{}\n'.format(ref)

        # Empty fn_lnk_refs
        self.fn_lnk_refs = []

        return refs


class LSMarkdown(Markdown):
    """Link Style Markdown parser.
    """

    def __init__(self, renderer=None, inline=None, block=None, **kwargs):
        link_style = kwargs.get('link_style') or 'inline'

        if not renderer:
            renderer = LSRenderer(link_style=link_style)
        if not inline:
            inline = LSInlineLexer(renderer)
        if not block:
            block = LSBlockLexer()

        super(LSMarkdown, self).__init__(renderer, inline, block, **kwargs)

    def parse(self, text):
        # Reset footnote link variables.
        self.renderer.fn_lnk_num = 0
        self.renderer.fn_lnk_refs = []

        # Parse text.
        out = super(LSMarkdown, self).parse(text)

        # Spit out.
        return out.lstrip('\n')


class LinkStyler(object):
    """Markdown Link Styler.

    """

    def __init__(self, link_style='inline'):
        self.style = link_style

    def __call__(self, file_):
        return self._link_stylize(file_)

    def _link_stylize(self, file_):
        text = file_.read()
        md = LSMarkdown(link_style=self.style)

        return md(text)


def _mdl_stylize(args):
    ls = LinkStyler(args.link_style)
    print(ls(args.file), end='')


def _get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('link_style', choices=['inline', 'footnote'],
                        help='Markdown Link style.')
    parser.add_argument('file', type=argparse.FileType('r'),
                        help='Path to Markdown file.')
    return parser.parse_args()


def main():
    args = _get_args()
    _mdl_stylize(args)
