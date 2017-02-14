"""
tmpld.core.template
~~~~~~~~~~~~~~

Jinja2 Template wrapper for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import shutil
import textwrap

from . import util, frontmatter


class Template(frontmatter.FrontMatterFile):
    def __init__(self, file):
        frontmatter.FrontMatterFile.__init__(self, file)
        self.rendered = False
        self.written = False
        self._set_defaults()

    def __repr__(self):
        return ('%s(%s, '
                'rendered: %s, written: %s, metadata: %s, content: %s)') % (
                    type(self).__name__,
                    self.file,
                    self.rendered,
                    self.written,
                    self.metadata,
                    textwrap.shorten(self.content, 60)
                )

    def _set_defaults(self):
        if not self.metadata.get('target'):
            if self.file.endswith('.j2'):
                self.metadata['target'] = self.file.rsplit('.', 1)[0]
            else:
                self.metadata['target'] = self.file
        if not self.metadata.get('owner'):
            self.metadata['owner'] = ':'.join(util.get_ownership(self.file))
        if not self.metadata.get('mode'):
            self.metadata['mode'] = util.get_mode(self.file)

    @property
    def target(self):
        return self.metadata.get('target')

    def save(self, check_rendered=True):
        """Write jinja template to disk with ownership and mode."""
        if check_rendered and not self.rendered:
            raise RuntimeError('Template: %s not rendered', self)
        target = self.metadata['target']
        owner = self.metadata['owner']
        mode = self.metadata['mode']
        with open(target, 'w') as fd:
            fd.write(self.content)
            if not self.content.endswith('\n'):
                fd.write('\n\n')
        shutil.chown(target, *util.parse_user_group(owner))
        os.chmod(target, util.octalize(mode))
