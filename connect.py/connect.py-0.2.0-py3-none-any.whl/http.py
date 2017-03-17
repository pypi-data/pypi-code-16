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

import requests
import json
import sys
import re

from .errors import HTTPSException, Unauthorized, Forbidden, NotFound
from . import utils, __version__


class HTTPClient:

    BASE = 'https://connect.monstercat.com'
    SIGNIN = BASE + '/signin'
    SIGNOUT = BASE + '/signout'
    API_BASE = BASE + '/api'
    SELF = API_BASE + '/self'
    CATALOG = API_BASE + '/catalog'
    PLAYLIST = API_BASE + '/playlist'
    TRACK = CATALOG + '/track'
    RELEASE = CATALOG + '/release'
    ARTIST = CATALOG + '/artist'

    def __init__(self):
        self.session = requests.Session()

        user_agent = 'ConnectBot (https://github.com/GiovanniMCMXCIX/connect.py {0}) ' \
                     'Python/{1[0]}.{1[1]} requests/{2}'
        self.user_agent = user_agent.format(__version__, sys.version_info, requests.__version__)

    def request(self, method, url, **kwargs):
        response = self.session.request(method, url, **kwargs)
        headers = {
            'User-Agent': self.user_agent,
        }

        if 'json' in kwargs:
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = utils.to_json(kwargs.pop('json'))

        kwargs['headers'] = headers
        try:
            if 'stream' in kwargs:
                if 300 > response.status_code >= 200:
                    return response
                elif response.status_code == 401:
                    raise Unauthorized('You are not authorized to perform this action.')
                elif response.status_code == 403:
                    raise Forbidden('You do not have permission to access this resource.')
                elif response.status_code == 404:
                    raise NotFound('Requested resource not found.')
                else:
                    raise HTTPSException(None, response)
            else:
                data = json.loads(response.text)

                if 300 > response.status_code >= 200:
                    return data
                elif response.status_code == 401:
                    raise Unauthorized(data.get('message', 'Unknown error'))
                elif response.status_code == 403:
                    raise Forbidden(data.get('message', 'Unknown error'))
                elif response.status_code == 404:
                    raise NotFound(data.get('message', 'Unknown error'))
                else:
                    message = None if not data.get('message', None) else data.get('message')
                    raise HTTPSException(message, response)
        except Exception as e:
            raise e

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('PUT', *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.request('PATCH', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('DELETE', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def email_signin(self, email, password):
        payload = {
            'email': email,
            'password': password
        }
        self.post(self.SIGNIN, json=payload)

    def two_feature_signin(self, email, password, token):
        payload = {
            'token': token
        }
        self.email_signin(email, password)
        self.post('{0.SIGNIN}/token'.format(self), json=payload)

    def is_singed_in(self):
        response = self.get('{0.SELF}/session'.format(self))
        if not response.get('user'):
            return False
        if response.get('user').get('subscriber', False) is True:
            return True

    def signout(self):
        self.post(self.SIGNOUT)

    def self(self):
        return self.get(self.SELF)

    def edit_profile(self, *, name=None, real_name=None, location=None, password=None):
        payload = {}
        if name:
            payload['name'] = name
        elif real_name:
            payload['realName'] = real_name
        elif location:
            payload['location'] = location
        elif password:
            payload['password'] = password
        return self.patch(self.SELF, json=payload)

    def add_reddit_username(self, username):
        payload = {
            'redditUsername': username
        }
        self.post('{0.SELF}/update-reddit'.format(self), json=payload)

    def get_discord_gold_invite(self):
        return self.get('{0.SELF}/discord/gold'.format(self))

    def download_release(self, album_id, path, audio_format):
        url = utils.DownloadLink().release(album_id, audio_format)
        r = self.get(url, stream=True)
        filename = str.replace(re.findall("filename=(.+)", r.headers['content-disposition'])[0], "\"", "")
        full_path = path + "/" + filename

        with open(full_path, 'wb') as file:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        return True

    def download_track(self, album_id, track_id, path, audio_format):
        url = utils.DownloadLink().track(album_id, track_id, audio_format)
        r = self.get(url, stream=True)
        filename = str.replace(re.findall("filename=(.+)", r.headers['content-disposition'])[0], "\"", "")
        full_path = path + "/" + filename

        with open(full_path, 'wb') as file:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
        return True

    def get_release(self, catalog_id):
        return self.get('{0.RELEASE}/{1}'.format(self, catalog_id))

    def get_release_tracklist(self, release_id):
        return self.get('{0.RELEASE}/{1}/tracks'.format(self, release_id))

    def get_track(self, track_id):
        return self.get('{0.TRACK}/{1}'.format(self, track_id))

    def get_artist(self, artist_id):
        return self.get('{0.ARTIST}/{1}'.format(self, artist_id))

    def get_artist_releases(self, artist_id):
        return self.get('{0.ARTIST}/{1}/releases'.format(self, artist_id))

    def get_playlist(self, playlist_id):
        return self.get('{0.PLAYLIST}/{1}'.format(self, playlist_id))

    def get_playlist_tracklist(self, playlist_id):
        return self.get('{0.PLAYLIST}/{1}/tracks'.format(self, playlist_id))

    def get_track_list(self):
        return self.get(self.TRACK)

    def get_release_list(self):
        return self.get(self.RELEASE)

    def get_artist_list(self):
        return self.get(self.ARTIST)

    def get_playlist_list(self):
        return self.get(self.PLAYLIST)

    def search_release(self, term, limit=None, skip=None):
        return self.get('{0.RELEASE}?fuzzyOr=title,{1},renderedArtists,{1}&limit={2}&skip{3}'.format(self, term, limit, skip))

    def search_release_advanced(self, title, artists, limit=None, skip=None):
        return self.get('{0.RELEASE}?fuzzy=title,{1},renderedArtists,{2}&limit={3}&skip{4}'.format(self, title, artists, limit, skip))
    
    def search_track(self, term, limit=None, skip=None):
        return self.get('{0.TRACK}?fuzzyOr=title,{1},artistsTitle,{1}&limit={2}&skip{3}'.format(self, term, limit, skip))
    
    def search_track_advanced(self, title, artists, limit=None, skip=None):
        return self.get('{0.TRACK}?fuzzy=title,{1},artistsTitle,{2}&limit={3}&skip{4}'.format(self, title, artists, limit, skip))

    def search_artist(self, term, limit=None, skip=None):
        return self.get('{0.ARTIST}?fuzzyOr=name,{1}&limit={2}&skip{3}'.format(self, term, limit, skip))

    def search_playlist(self, term, limit=None, skip=None):
        return self.get('{0.PLAYLIST}?fuzzyOr=name,{1}&limit={2}&skip{3}'.format(self, term, limit, skip))
