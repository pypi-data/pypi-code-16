# -*- coding: utf-8 -*-
"""
    A Directive for displaying multiple tabbed code blocks.

    Based largely off of `configurationblock`:
    https://github.com/fabpot/sphinx-php/
    copyright 2010-2012 Fabien Potencier (MIT license)

    :copyright: (c) 2016 Neumitra Inc.
    :license: Apache 2, see LICENSE for more details.
"""

import pkg_resources
from docutils.parsers.rst import Directive, directives
from docutils import nodes
from sphinx.application import ExtensionError


class multisource(nodes.General, nodes.Element):
    pass


class Multisource(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}
    formats = {
        'java': 'Java',
        'javascript': 'Javascript',
        'objc': 'Objective-C',
        'python': 'Python',
        'clojure': 'Clojure'
    }

    def __init__(self, *args):
        Directive.__init__(self, *args)
        env = self.state.document.settings.env
        multisource_block = env.app.config.multisource_block

        for language in multisource_block:
            self.formats[language] = multisource_block[language]

    def run(self):
        env = self.state.document.settings.env

        node = nodes.Element()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)

        entries = []
        for i, child in enumerate(node):
            if isinstance(child, nodes.literal_block):
                # add a title (the language name) before each block
                targetid = "multisource-%d" % env.new_serialno('multisource')
                targetnode = nodes.target('', '', ids=[targetid])
                targetnode.append(child)
                if 'language' in child:
                    language = child['language']
                else:
                    language = env.app.config.highlight_language

                innernode = nodes.emphasis(self.formats[language], self.formats[language])

                para = nodes.paragraph()
                para += [innernode, child]

                entry = nodes.list_item('')
                entry.append(para)
                entries.append(entry)

        resultnode = multisource()
        resultnode.append(nodes.bullet_list('', *entries))

        return [resultnode]

def visit_multisource_html(self, node):
    self.body.append(self.starttag(node, 'div', CLASS='multisource'))

def depart_multisource_html(self, node):
    self.body.append('</div>\n')

def visit_multisource_latex(self, node):
    pass

def depart_multisource_latex(self, node):
    pass

def builder_inited(app):
    js = pkg_resources.resource_filename('thriftdomain', 'static/ext.js')
    css = pkg_resources.resource_filename('thriftdomain', 'static/ext.css')
    app.add_javascript(js)
    app.add_stylesheet(css)

def setup(app):
    app.add_node(multisource,
                 html=(visit_multisource_html, depart_multisource_html),
                 latex=(visit_multisource_latex, depart_multisource_latex))
    app.add_directive('multisource', Multisource)
    app.add_config_value('multisource_block', {}, 'env')
    app.connect('builder-inited', builder_inited)
