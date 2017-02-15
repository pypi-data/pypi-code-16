# !/usr/bin/env python
# -*- coding:utf-8 -*-


# Copyright (C) 2016  Tony Kamillo

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, requests, shelve, hashlib, json, subprocess, shutil, argparse, urllib
from flask import Flask, request, redirect, make_response
from slugify import slugify

base_dir = os.path.dirname(os.path.abspath(__file__))

api = 'https://api.spotify.com/v1'

client_id = '29dc7e19acb9434dbd39701cc6db83dc'
client_secret = '0a7c3827ca6e493281e025b596f7d100'

app = Flask(__name__)


def cmd(command):
    output, error = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()

    if error:
        print(error)

    return output


def touch(filename):
    f = open(filename, 'a')
    f.close()


class Store(object):

    def __init__(self, name):

        store_file = os.path.join(base_dir, '%s.data' % name)
        self.__store = shelve.open(store_file)

    def get(self, key):
        return self.__store.get(key)

    def add(self, key, value):
        self.__store[key] = value
        self.__store.sync()
        return self

    def close(self):
        self.__store.close()


class Credentials(object):

    def __init__(self):
        self.__filename = os.path.join(base_dir, 'spotify_credentials')

        if not os.path.exists(self.__filename):
            touch(self.__filename)

        self.__params = self.__get_params()

    def __get_params(self):
        content = ''
        with open(self.__filename) as f:
            content = f.read()
            if not content:
                content = '{}'
        return json.loads(content)

    def __reload_params(self):
        self.__params = None
        self.__params = self.__get_params()

    @property
    def params(self):
        return self.__params

    def update(self, data={}):
        credentials_copy = self.params
        credentials_copy.update(data)
        json.dump(credentials_copy, open(self.__filename, 'w'), indent=4)

    def refresh_access_token(self):
        auth = '%s:%s' % (client_id, client_secret)
        headers = {'Authorization': 'Basic %s' % auth.encode('base64').replace('\n', '')}
        params = {'grant_type': 'refresh_token', 'refresh_token': self.params.get('refresh_token')}

        r = requests.post('https://accounts.spotify.com/api/token', data=params, headers=headers)
        return r.json().get('access_token')

    def refresh(self):
        print('Refreshing...')
        access_token = self.refresh_access_token()
        self.update({'access_token': access_token})
        self.__reload_params()

    def check_auth_tokens(self):
        error = ''
        if not self.params.get('refresh_token'):
            error = 'Please run ./spotify_dl.py --authorize to get the authorization tokens.'
        return error

    def check(self):
        return [check_error() for check_error in [self.check_auth_tokens] if check_error()]


class Spotify(object):

    def __init__(self, credentials=None):
        self.__reload_credentials(credentials)

    def __reload_credentials(self, credentials=None):
        self.__credentials = credentials or Credentials()
        self.__user_id = self.__credentials.params.get('user_id')
        self.__access_token = self.__credentials.params.get('access_token')
        self.__bearer_headers = {'Authorization': 'Bearer %s' % self.__access_token}

    def __has_error(self, obj):
        error = obj.get('error')
        check = bool(error and error.get('status') == 401)
        if check:
            print('Refreshing credentials.')
            print(error)
            self.__credentials.refresh()
            self.__reload_credentials()
        return check

    def playlists(self):
        r = requests.get(api + '/me/playlists?offset=0&limit=30', headers=self.__bearer_headers)
        playlists_data = r.json()

        if self.__has_error(playlists_data):
            playlists_data = self.playlists()

        return playlists_data

    def playlist_tracks(self, playlist):
        url = playlist.get('tracks', {}).get('href') if isinstance(playlist, dict) \
            else api + '/users/%s/playlists/%s/tracks' % (self.__user_id, playlist)

        r = requests.get(url, headers=self.__bearer_headers)
        tracks = r.json()

        if self.__has_error(tracks):
            tracks = self.playlist_tracks(playlist)

        return tracks


def normalize(filename):
    return filename.replace('Various Artists - ', '').replace('(', '[').replace(')', ']').replace('/', '-')


def extract_saved_name(output):
    name = ''
    for line in output.split('\n'):
        prefix = '[ffmpeg] Destination:'
        if line.startswith(prefix):
            name = line.replace(prefix, '').strip()
            break

    return name


def download_tracks(folder, playlists='ALL'):
    print('\n')

    credentials = Credentials()
    spotify = Spotify(credentials)

    for playlist in spotify.playlists().get('items'):

        if playlists == 'ALL' or playlist.get('name') in playlists:
            print('# %s' % playlist.get('name'))

            tracks = spotify.playlist_tracks(playlist)
            for track_item in tracks.get('items', []):

                track = track_item.get('track')
                name = slugify(track.get('name'), separator=' ')
                album = slugify(track.get('album').get('name'), separator=' ')
                artist = slugify(track.get('artists')[0].get('name'), separator=' ')
                music_identifier = '%s - %s' % (artist, name)
                if name == album:
                    music_identifier = '%s song' % music_identifier
                music_identifier = normalize(music_identifier)
                destination_filename = normalize('%s - %s - %s' % (artist, album, name))

                download(folder, normalize(playlist.get('name')), music_identifier, destination_filename)

            print('\n')
    print('\t=========================================================================================================')
    print('\nDownloads is done.')


def instantmusic_cmd():

    locations = [
        os.path.join(os.environ.get('VIRTUAL_ENV', '__NO_VIRTUAL_ENV__'), 'bin', 'instantmusic'),
        '/usr/local/bin/instantmusic',
        '/usr/bin/instantmusic'
    ]

    instantmusic = None

    for path in locations:
        if os.path.exists(path):
            instantmusic = path
            break

    return instantmusic


def download(dest_folder, playlist_name, music_identifier, destination_filename):

    playlist_folder = os.path.join(dest_folder, playlist_name)
    if not os.path.exists(playlist_folder):
        os.mkdir(playlist_folder)

    destfile = os.path.join(playlist_folder, '%s.mp3' % destination_filename)

    store = Store('downloaded')
    key = hashlib.md5(destination_filename.encode('u8')).hexdigest()
    filename = store.get(key)

    if filename and os.path.exists(filename):
        if filename != destfile:
            shutil.copy(filename, destfile)

    else:
        os.chdir(playlist_folder)

        print('\tDownloading: %s' % music_identifier)

        instantmusic = instantmusic_cmd()
        if not instantmusic:
            raise Exception(u'Instantmusic module is required. Please run "pip install instantmusic"')

        cmdline = '%s -s %s -p' % (instantmusic, music_identifier.encode('u8'))
        # print(cmdline)
        output = cmd(cmdline)
        # print(output)
        name = extract_saved_name(output)
        print('\t%s' % name)
        old = os.path.join(playlist_folder, name.decode('u8'))
        print('\t%s -> %s' % (old, destfile))
        os.rename(old, destfile)

    store.add(key, destfile)
    store.close()

    print('\tSaved at %s' % destfile)
    print('\t---------------------------------------------------------------------------------------------------------')


def its_ok(checker):

    errors = checker()

    if errors:
        print('\n')
        if isinstance(errors, list):
            for error in errors:
                print('[WARNING]: %s' % error)
        else:
            print('[WARNING]: %s' % errors)
        print('\n')

    return bool(not errors)


def expanded_path(path):
    realpath = os.path.expandvars(path)
    realpath = os.path.expanduser(realpath)
    realpath = os.path.abspath(realpath)
    return realpath


@app.route('/')
def index():
    uri = 'https://accounts.spotify.com/authorize?' + urllib.urlencode({
        'response_type': 'code',
        'client_id': client_id,
        'scope': 'user-read-private user-read-email playlist-read-private playlist-read-collaborative',
        'redirect_uri': 'http://localhost:5000/callback',
        'state': os.urandom(16).encode('base64')
    })

    return redirect(uri)


@app.route('/callback')
def callback():
    creds = Credentials()
    url = 'https://accounts.spotify.com/api/token'
    params = {
        'code': request.args.get('code'),
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:5000/callback'
    }
    auth = '%s:%s' % (client_id, client_secret)

    print(auth)

    headers = {'Authorization': 'Basic %s' % auth.encode('base64').replace('\n', '')}

    r = requests.post(url, data=params, headers=headers)
    data = r.json()

    response = '''
    <div style="padding: 20px; margin: 0 auto; display: table; border-radius: 5px; background: #eee;">
        <h1 style="color: #009900; font-family: Verdana;">All right.</h1>
        <p style="color: #444; font-family: Verdana;">SpotifyDL was authorized to access your Spotify account information.</p>
        <p style="color: #444; font-family: Verdana;">Now go to terminal press ctrl+c and starts to download your musics.</p>
        <p style="color: #444; font-family: Verdana;">For more information execute spotify_dl -h</p>
    </div>
    '''

    error = data.get('error')
    if error:
        response = make_response(json.dumps(error))
        response.headers['ContentType'] = 'text/json'
    else:
        creds.update({
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token')
        })

    return response


def main():
    parser = argparse.ArgumentParser(description='Spotify downloader tool.')

    parser.add_argument('-d', '--download-folder', help='Folder path to where you want saving the downloaded musics.')
    parser.add_argument('-p', '--playlists', help='Playlists (separated by comma) what you wanna to download. DEFAULT: ALL', default='ALL')
    parser.add_argument('-auth', '--authorize', action='store_true', help='Getting authorization from spotify')

    args = parser.parse_args()

    creds = Credentials()
    if args.authorize:
        user_id = creds.params.get('user_id')

        if not user_id:
            user_id = raw_input('Insert your Spotify username: ')
            user_id = user_id.strip()
            creds.update({'user_id': user_id})

        if user_id:
            print('\n')
            print('##########################################################')
            print('## Open your web browser and go to http://localhost:5000 ##')
            print('##########################################################')
            print('\n')
            app.run()
    else:
        folder = args.download_folder
        if not folder:
            folder = raw_input('Insert the path where you want to save the downloaded playlists: ')
            folder = folder.strip()

        playlists = args.playlists if args.playlists == 'ALL' else args.playlists.split(',')

        if its_ok(creds.check):
            download_tracks(expanded_path(folder), playlists)


if __name__ == '__main__':
    main()
