from bs4 import BeautifulSoup
from datetime import datetime
import json

from bandcamp_dl.bandcampjson import BandcampJSON
from bandcamp_dl.bandcamp import Bandcamp

mockups = "./mockups"


class TestClass:
    def test_track(self):
        print("\nTesting supported sources")
        with open("{}/track.html".format(mockups), encoding="utf8") as f:
            source = f.read()
            soup = BeautifulSoup(source, "html.parser")

            # Grab the embed and album data
            embed = BandcampJSON(soup, "EmbedData")
            album = BandcampJSON(soup, "TralbumData")

            # Format the raw js into a json string
            embed_raw = embed.js_to_json()
            album_raw = album.js_to_json()

            # Load the json string as a json object
            embed_json = json.loads(embed_raw)
            album_json = json.loads(album_raw)

            # list of tracks in the album
            tracks = album_json['trackinfo']

            # Build the album dict
            album_release = album_json['album_release_date']
            if album_release is None:
                album_release = album_json['current']['release_date']
                assert album_release == "null"
            else:
                assert album_release == "09 Sep 2016 00:00:00 GMT"

            album_title = album_json['trackinfo'][0]['title']
            assert album_title == "Hold My Head"

            album = {
                "tracks": [],
                "title": album_title,
                "artist": embed_json['artist'],
                "full": False,
                "art": "",
                "date": datetime.strptime(album_release, "%d %b %Y %X %Z").strftime("%m%d%Y")
            }

            for track in tracks:
                if track['file'] is not None:
                    track = Bandcamp.get_track_metadata(track)
                    album['tracks'].append(track)

    def test_album(self):
        with open("{}/album.html".format(mockups), encoding="utf8") as f:
            source = f.read()
            soup = BeautifulSoup(source, "html.parser")

            # Grab the embed and album data
            embed = BandcampJSON(soup, "EmbedData")
            album = BandcampJSON(soup, "TralbumData")

            # Format the raw js into a json string
            embed_raw = embed.js_to_json()
            album_raw = album.js_to_json()

            # Load the json string as a json object
            embed_json = json.loads(embed_raw)
            album_json = json.loads(album_raw)

            # list of tracks in the album
            tracks = album_json['trackinfo']

            # Build the album dict
            album_release = album_json['album_release_date']
            assert album_release == "09 Sep 2016 00:00:00 GMT"

            album_title = embed_json['album_title']
            assert album_title == "The Long Dark Blue"

            album = {
                "tracks": [],
                "title": album_title,
                "artist": embed_json['artist'],
                "full": False,
                "art": "",
                "date": datetime.strptime(album_release, "%d %b %Y %X %Z").strftime("%m%d%Y")
            }

            for track in tracks:
                if track['file'] is not None:
                    track = Bandcamp.get_track_metadata(track)
                    album['tracks'].append(track)

    def test_artist(self):
        with open("{}/artist.html".format(mockups), encoding="utf8") as f:
            source = f.read()
            soup = BeautifulSoup(source, "html.parser")

            # Grab the embed and album data
            embed = BandcampJSON(soup, "EmbedData")
            album = BandcampJSON(soup, "TralbumData")

            # Format the raw js into a json string
            embed_raw = embed.js_to_json()
            album_raw = album.js_to_json()

            # Load the json string as a json object
            embed_json = json.loads(embed_raw)
            album_json = json.loads(album_raw)

            # list of tracks in the album
            tracks = album_json['trackinfo']

            # Build the album dict
            album_release = album_json['album_release_date']
            assert album_release == "09 Sep 2016 00:00:00 GMT"

            album_title = embed_json['album_title']
            assert album_title == "The Long Dark Blue"

            album = {
                "tracks": [],
                "title": album_title,
                "artist": embed_json['artist'],
                "full": False,
                "art": "",
                "date": datetime.strptime(album_release, "%d %b %Y %X %Z").strftime("%m%d%Y")
            }

            for track in tracks:
                if track['file'] is not None:
                    track = Bandcamp.get_track_metadata(track)
                    album['tracks'].append(track)