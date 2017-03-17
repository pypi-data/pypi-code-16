# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2016-2017 GiovanniMCMXCIX

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .http import HTTPClient
from .release import Release


class Artist:
    """Represents a release from connect.

    Attributes
    ----------
    id : str
        The artist ID.
    name : str
        The artist name.
    vanity_uri : str
        The artist vanity uri.
    profile_image_id : int
        The profile image hash the artist has. Could be None.
    urls : list
        The artist social media urls.
    years : list
        The artist release years.
    """

    __slots__ = [
        'id', 'name', 'vanity_uri', 'profile_image_id', 'about', 'urls', 'years', '_profile_image_url', '_releases'
    ]

    def __init__(self, **kwargs):
        self.id = kwargs.pop('_id')
        self.name = kwargs.pop('name')
        self.vanity_uri = kwargs.pop('vanityUri', None)
        self.profile_image_id = kwargs.pop('profileImageBlobId', None)
        self._profile_image_url = kwargs.pop('profileImageUrl')
        self.about = kwargs.pop('about', None)
        self.urls = kwargs.pop('urls')
        self.years = kwargs.pop('years')
        self._releases = {}

    def __str__(self):
        return self.name

    def _add_release(self, release):
        self._releases[release.id] = release

    @property
    def profile_image_url(self):
        """Returns a friendly URL version of the profile_image_id variable the artist has."""
        if not self.profile_image_id:
            return self._profile_image_url
        else:
            return 'http://blobcache.monstercat.com/blobs/{0.profile_image_id}'.format(self)

    @property
    def releases(self):
        """Returns a list of connect.Release items."""
        if self._releases:
            return self._releases.values()
        else:
            for r_data in HTTPClient().get_artist_releases(self.id)['results']:
                release = Release(**r_data)
                self._add_release(release)
            return self._releases.values()


class ArtistEntry:
    """Represents an artist entry from a track.

    Attributes
    ----------
    id : str
        The artist ID.
    name : str
        The artist name.
    """

    __slots__ = ['id', 'name']

    def __init__(self, **kwargs):
        self.id = kwargs.pop('artistId')
        self.name = kwargs.pop('name')

    def __str__(self):
        return self.name
