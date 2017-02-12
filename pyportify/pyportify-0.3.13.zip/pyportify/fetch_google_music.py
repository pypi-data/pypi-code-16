#!/usr/bin/env python3

import asyncio
import ssl
from getpass import getpass
import sys

import aiohttp
from aiohttp import ClientSession
import certifi

from pyportify import app
from pyportify.google import Mobileclient
from pyportify.spotify import SpotifyClient
from pyportify.util import uprint

try:
    input = raw_input
except NameError:
    pass

OAUTH_URL = \
    "https://developer.spotify.com/web-api/console/get-playlist-tracks/"


@asyncio.coroutine
def start():

    sslcontext = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl_context=sslcontext)

    with ClientSession(connector=conn) as session:

        google_email = "rckclmbr@gmail.com"
        google_pass = "evvqmjgsqddsdttm"

        g = Mobileclient(session)

        logged_in = yield from g.login(google_email, google_pass)
        if not logged_in:
            uprint("Invalid Google username/password")
            sys.exit(1)

        spotify_token = "BQANs1yfZUBAtT1kf2UlW0e_bJQUpFbKw9OzP6qxGpSaKRqUKJTYb_ulau0988wvvUtT-3vTZY0mfzZokztsZT5yhsj3xAHgiFE9Xm0L4ZzPQMxECr6jDnQEYpNi0GjH5_mo35ewAweOhD8-wU_UwQDPNBFtulafLIH-NKP7x41zdEtEKM32PvKeJQ0ykK62776tCBOOFs0B24p0cMt3Aq7Iange3VWS1r66_-pXGmoeUfqptAD9ZqZngR82GL56wgHE0Z6XtJ_03tSicjXeupzVMBLSojjDzKFv6pE3vg8x6rfMjDgT"

        s = SpotifyClient(session, spotify_token)

        logged_in = yield from s.loggedin()
        if not logged_in:
            uprint("Invalid Spotify token")
            sys.exit(1)



        # di = yield from g.fetch_playlists()
        # import pprint
        # pprint.pprint(di['data']['items'])
        #
        # # playlist_id = yield from g.create_playlist("Test Playlist")
        # playlist_id = "2c02eca1-429e-4ce0-a4a8-819415cdee3a"
        # yield from g.add_songs_to_playlist(
        #     playlist_id,
        #     ['Twqujxontbfftlzi7hextragxyu'],
            # ['ba3a473e-6309-3814-8c05-b8b6619f38f3'],
        # )
        playlists = yield from s.fetch_spotify_playlists()
        playlists = [l['uri'] for l in playlists]
        yield from app.transfer_playlists(None, s, g, playlists)


def main():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start())
    finally:
        loop.close()


if __name__ == '__main__':
    main()
