"""
tmpld.core.environment
~~~~~~~~~~~~~~

Jinja2 environment for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import json
import io
import re

import yaml
import jinja2
import jsonpath_rw

import pyrkube
import pycaps

from . import util


class TemplateEnvironment:
    defaults = dict(
        options=dict(
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False
        ),
        glbls=dict(
            env=os.environ,
            shell=util.shell,
            json=json,
            yaml=yaml,
            xpath=util.xpath,
            re=re,
            jpath=jsonpath_rw.parse
        )
    )

    def __init__(self, glbls=None, options=None, strict=False, **kwargs):
        self.options = util.set_defaults(options, self.defaults['options'])
        self.glbls = util.set_defaults(glbls, self.defaults['glbls'])
        self.env = jinja2.Environment(**self.options)
        if strict:
            self.env.undefined = jinja2.StrictUndefined
        self.env.globals.update(self.glbls)

    def render(self, template):
        if not template.rendered:
            template.original = template.content
            template.content = self.env.from_string(template.content).render()
            template.rendered = True
        return template
