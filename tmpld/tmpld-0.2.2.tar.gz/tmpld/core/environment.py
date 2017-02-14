"""
tmpld.core.environment
~~~~~~~~~~~~~~

Jinja2 environment for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import io
import re
import json
import yaml

import jinja2
from jinja2 import FileSystemLoader

from . import util, tags
from .util import try_import


class TmpldEnvironment(jinja2.environment.Environment):
    def from_string(self, source, filename=None, globals=None,
                    template_class=None):
        globals = self.make_globals(globals)
        globals['filename'] = filename
        globals['dirname'] = os.path.dirname(filename)
        cls = template_class or self.template_class
        return cls.from_code(
            self, self.compile(source, filename=filename), globals, None
        )


class TemplateEnvironment:
    defaults = dict(
        options=dict(
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
            extensions=[tags.FileTag]
        ),
        glbls=dict(
            env=os.environ,
            shell=util.shell,
            file=util.get_file,
            json=json,
            re=re,
            yaml=yaml,
            xpath=util.xpath,
            jpath=util.jpath
        )
    )

    def __init__(self, glbls=None, files=None, options=None, strict=False,
                 **kwargs):
        self.files = files
        self.options = util.set_defaults(options, self.defaults['options'])
        self.options['loader'] = FileSystemLoader(
            util.get_dirs(files),
            followlinks=True
        )
        self.glbls = util.set_defaults(glbls, self.defaults['glbls'])
        self.env = TmpldEnvironment(**self.options)
        if strict:
            self.env.undefined = jinja2.StrictUndefined
        self.env.globals.update(self.glbls)

    def render(self, template):
        if not template.rendered:

            template.original = template.content
            template._template = self.env.from_string(
                template.content, template.file
            )
            template.content = template._template.render()
            template.rendered = True
        return template
