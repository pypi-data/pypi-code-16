# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Batch Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import os
import stat
import random

import formalchemy as fa
from formalchemy.ext import fsblob
from formalchemy.fields import FileFieldRenderer as Base
from webhelpers.html import tags


class BatchIDFieldRenderer(fa.FieldRenderer):
    """
    Renderer for batch ID fields.
    """
    def render_readonly(self, **kwargs):
        try:
            batch_id = self.raw_value
        except AttributeError:
            # this can happen when creating a new batch, b/c the default value
            # comes from a sequence
            pass
        else:
            if batch_id:
                return '{:08d}'.format(batch_id)
        return ''


# TODO: make this inherit from `tailbone.forms.renderers.files.FileFieldRenderer`
class FileFieldRenderer(fsblob.FileFieldRenderer):
    """
    Custom file field renderer for batches based on a single source data file.
    In edit mode, shows a file upload field.  In readonly mode, shows the
    filename and its size.
    """

    @classmethod
    def new(cls, view):
        name = 'Configured%s_%s' % (cls.__name__, str(random.random())[2:])
        return type(str(name), (cls,), dict(view=view))

    @property
    def storage_path(self):
        return self.view.upload_dir

    def get_size(self):
        size = super(FileFieldRenderer, self).get_size()
        if size:
            return size
        batch = self.field.parent.model
        path = os.path.join(self.view.handler.datadir(batch), self.field.value)
        if os.path.isfile(path):
            return os.stat(path)[stat.ST_SIZE]
        return 0

    def get_url(self, filename):
        batch = self.field.parent.model
        return self.view.request.route_url('{}.download'.format(self.view.get_route_prefix()),
                                           uuid=batch.uuid)

    def render(self, **kwargs):
        return Base.render(self, **kwargs)


class HandheldBatchFieldRenderer(fa.FieldRenderer):
    """
    Renderer for inventory batch's "handheld batch" field.
    """

    def render_readonly(self, **kwargs):
        batch = self.raw_value
        if batch:
            return tags.link_to(
                batch.id_str,
                self.request.route_url('batch.handheld.view', uuid=batch.uuid))
        return ''
