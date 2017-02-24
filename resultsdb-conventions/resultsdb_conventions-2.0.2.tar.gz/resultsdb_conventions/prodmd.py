# Copyright (C) Red Hat Inc.
#
# resultsdb_conventions is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:   Adam Williamson <awilliam@redhat.com>

"""Conventions for tests of items with productmd-style metadata."""

from __future__ import unicode_literals
from __future__ import print_function

# stdlib imports
import json
import logging

# external imports
import productmd.composeinfo

# internal imports
from .base import Result

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)


class ProductmdComposeResult(Result):
    """Result from testing of a distribution compose with productmd
    style metadata. composeinfo must be the composeinfo metadata for
    the compose as a dict or a JSON string.
    """
    def __init__(self, composeinfo, *args, **kwargs):
        super(ProductmdComposeResult, self).__init__(*args, **kwargs)
        try:
            # already dict-ified
            composeinfo['header']
            self.composeinfo = composeinfo
        except TypeError:
            # JSON string
            self.composeinfo = json.loads(composeinfo)
        self.cid = self.composeinfo['payload']['compose']['id']
        # item is always the compose ID (unless subclass overrides)
        self.extradata.update({
            'item': self.cid,
            'type': 'compose',
        })
        self.conventions.append('productmd.compose')

    def default_extradata(self):
        """Add values from the metadata."""
        super(ProductmdComposeResult, self).default_extradata()
        extradata = {
            'productmd.compose.name': self.composeinfo['payload']['release']['name'],
            'productmd.compose.short': self.composeinfo['payload']['release']['short'],
            'productmd.compose.version': self.composeinfo['payload']['release']['version'],
            'productmd.compose.date': self.composeinfo['payload']['compose']['date'],
            'productmd.compose.type': self.composeinfo['payload']['compose']['type'],
            'productmd.compose.respin': self.composeinfo['payload']['compose']['respin'],
            'productmd.compose.id': self.cid,
        }
        extradata.update(self.extradata)
        self.extradata = extradata

    def default_groups(self):
        """Add to generic result group for this compose."""
        super(ProductmdComposeResult, self).default_groups()
        self.add_group('compose', self.cid)
        if self.source:
            self.add_group(self.source, self.cid)


class ProductmdImageResult(ProductmdComposeResult):
    """Result from testing a specific image in a distribution compose
    with productmd-style metadata. imgdict is the productmd image dict
    for the image.
    """
    def __init__(self, imgdict, *args, **kwargs):
        super(ProductmdImageResult, self).__init__(*args, **kwargs)
        self.imgdict = imgdict
        # assume / always used as path separator in productmd
        self.filename = imgdict['path'].split('/')[-1]
        # when we have an image, item is always the filename
        self.extradata.update({
            'item': self.filename,
        })
        self.conventions.append('productmd.image')

        # unique image identifier, per discussion at
        # https://pagure.io/pungi/issue/525 ; again, perhaps in the
        # long term this should be defined in productmd
        self.imgid = '.'.join((self.imgdict['subvariant'], self.imgdict['type'], self.imgdict['format'],
                               self.imgdict['arch'], str(self.imgdict['disc_number']))).lower()

    def default_extradata(self):
        """Populate extradata from compose ID and filename."""
        super(ProductmdImageResult, self).default_extradata()
        extradata = {
            'productmd.image.arch': self.imgdict['arch'],
            'productmd.image.disc_number': str(self.imgdict['disc_number']),
            'productmd.image.format': self.imgdict['format'],
            'productmd.image.subvariant': self.imgdict['subvariant'],
            'productmd.image.type': self.imgdict['type'],
        }
        extradata.update(self.extradata)
        self.extradata = extradata

    def default_groups(self):
        """Add to generic result group for this image."""
        super(ProductmdImageResult, self).default_groups()
        self.add_group('image', self.imgid)
        if self.source:
            # We cannot easily do a URL here, unless we start having
            # a store of 'known' sources and how URLs are built for
            # them, or using callbacks, or something. I think we might
            # just ask downstreams to get the group from the group
            # list and add the URL to it?
            self.add_group(self.source, self.imgid)

# vim: set textwidth=120 ts=8 et sw=4:
