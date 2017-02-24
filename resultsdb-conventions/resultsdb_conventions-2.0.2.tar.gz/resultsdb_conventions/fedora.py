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

"""Fedora-specific conventions."""

from __future__ import unicode_literals
from __future__ import print_function

# stdlib imports
import logging

# external imports
from cached_property import cached_property
import fedfind.release

# internal imports
from .base import Result
from .prodmd import (ProductmdComposeResult, ProductmdImageResult)

# pylint:disable=invalid-name
logger = logging.getLogger(__name__)


class FedoraComposeResult(ProductmdComposeResult):
    """Result from a test of a Fedora compose in general (not related
    to a specific deliverable). Functionally, just adds a URL to the
    compose group. Expects compose discovery from the compose ID, via
    fedfind: cid is the compose ID. May raise ValueError directly or
    via get_release.
    """
    def __init__(self, cid, *args, **kwargs):
        self.cid = cid
        composeinfo = self.ffrel.metadata['composeinfo']
        super(FedoraComposeResult, self).__init__(composeinfo, *args, **kwargs)
        self.conventions.append('fedora.compose')

    def default_groups(self):
        super(FedoraComposeResult, self).default_groups()
        # update the existing compose group with a URL
        try:
            rel = fedfind.release.get_release(cid=self.cid)
            self.add_group('compose', self.cid, ref_url=self.ffrel.location)
        except ValueError:
            logger.warning("fedfind found no release for compose ID %s, compose group will have no URL", self.cid)
            return

    @cached_property
    def ffrel(self):
        """Cached instance of fedfind release object."""
        return fedfind.release.get_release(cid=self.cid)


class FedoraImageResult(ProductmdImageResult, FedoraComposeResult):
    """Result from testing a specific image from a Fedora compose.
    filename is the image filename. cid is the compose ID (explicitly
    taken here as we need to use it before calling the parent class
    __init__). If imgdict is not provided, will use fedfind to find it
    from the filename.
    """
    def __init__(self, filename, cid, imgdict=None, *args, **kwargs):
        self.cid = cid
        self.filename = filename
        if not imgdict:
            imgdict = self.ffimg
        super(FedoraImageResult, self).__init__(imgdict, cid, *args, **kwargs)
        self.filename = filename
        self.conventions.append('fedora.image')

    @cached_property
    def ffimg(self):
        """Cached instance of fedfind image dict."""
        try:
            # this just gets the first image found by the expression,
            # we expect there to be maximum one (per dgilmore, image
            # filenames are unique at least until koji namespacing)
            return next(_img for _img in self.ffrel.all_images if _img['path'].endswith(self.filename))
        except StopIteration:
            # this happens if the expression find *no* images
            raise ValueError("Can't find image {0} in release {1}".format(self.filename, self.cid))


class FedoraBodhiResult(Result):
    """Result from testing a Fedora Bodhi update. update is the
    update ID.
    """
    def __init__(self, update, *args, **kwargs):
        self.update = update
        super(FedoraBodhiResult, self).__init__(*args, **kwargs)
        self.conventions.append('fedora.bodhi')
        self.extradata.update({
            'item': self.update,
            'type': 'bodhi_update',
        })

    def default_groups(self):
        super(FedoraBodhiResult, self).default_groups()
        url = 'https://bodhi.fedoraproject.org/updates/{0}'.format(self.update)
        self.add_group('bodhi', self.update, ref_url=url)
        if self.source:
            self.add_group(self.source, self.update)

# vim: set textwidth=120 ts=8 et sw=4:
