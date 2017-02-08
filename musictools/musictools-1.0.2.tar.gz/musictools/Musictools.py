#!/usr/bin/env python

"""
 __  __           _   _______          _     
|  \/  |         (_) |__   __|        | |    
| \  / |_   _ ___ _  ___| | ___   ___ | |___ 
| |\/| | | | / __| |/ __| |/ _ \ / _ \| / __|
| |  | | |_| \__ \ | (__| | (_) | (_) | \__ \
|_|  |_|\__,_|___/_|\___|_|\___/ \___/|_|___/

License : MIT 
https://github.com/lakshaykalbhor/MusicTools  

Musictools provides tools to:
1. Download music
ie : Provide song title -> Get youtube list -> Download song

2. Repair song titles by removing meaningless words
ie : Hey Jude (official lyrics) -> Hey Jude

3. Add metadata to music.
ie : Album art, correct title, album, artist, lyrics. (Using Spotify)
"""

# Internal Dependencies
import re
import json
from collections import OrderedDict
from urllib.parse import quote
from urllib.request import urlopen
from os.path import splitext

# External Dependencies
import youtube_dl
import requests
import spotipy
from bs4 import BeautifulSoup
from mutagen.mp3 import EasyMP3
from mutagen.id3 import ID3, APIC, _util


class MusicNow(object):
    """
    Fetch a list of youtube videos for a query,
    download the audio from chosen youtube video.
    """

    YOUTUBECLASS = 'spf-prefetch'

    def __init__(self):
        pass

    @staticmethod
    def get_url(song_input):
        """
        Given a song title, returns a list of 
        youtube videos found
        """

        html = requests.get("https://www.youtube.com/results",
                            params={'search_query': song_input})
        soup = BeautifulSoup(html.text, 'html.parser')

        youtube_list = OrderedDict()

        # In all Youtube Search Results

        for i in soup.findAll('a', {'rel': MusicNow.YOUTUBECLASS}):
            song_url = 'https://www.youtube.com' + (i.get('href'))
            song_title = (i.get('title'))
            youtube_list.update({song_title: song_url})

        return youtube_list

    @staticmethod
    def download_song(song_url, song_title, location):
        """
        Given a youtube url, downloads the song in a specified 
        location.
        """
        outtmpl = song_title + '.%(ext)s'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': location + outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {'key': 'FFmpegMetadata'},],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(song_url, download=True)


class MusicRepair(object):
    """
    Get metadata and album art for a particular song title,
    add metadata and album art to .mp3 file
    """

    def __init__(self):
        pass

    @staticmethod
    def get_details_spotify(file_name):
        """
        Tries finding metadata through Spotify
        """

        song_name = improve_name(file_name) #Remove words such as HD, Official, etc from title

        spotify = spotipy.Spotify()
        results = spotify.search(song_name, limit=1)
        try:
            results = results['tracks']['items'][0]  # Find top result
            album = (results['album']
                     ['name'])  # Parse json dictionary
            artist = (results['album']['artists'][0]['name'])
            song_title = (results['name'])
            albumart = (results['album']['images'][0]['url'])

            return artist, album, song_title, albumart, ''

        except Exception as error:
            return ' ', ' ', song_name, None, error

    @staticmethod
    def add_albumart(file_name, song_title=None, albumart=None):

        if albumart is None:
            albumart = img_search_google(song_title)
        else:
            pass
        try:
            img = urlopen(albumart)  # Gets album art from url

        except Exception:
            return None

        audio = EasyMP3(file_name, ID3=ID3)
        try:
            audio.add_tags()
        except _util.error:
            pass

        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/png',
                type=3,  # 3 is for album art
                desc='Cover',
                data=img.read()  # Reads and adds album art
            )
        )
        audio.save()

        return albumart

    @staticmethod
    def add_details(file_name, title, artist, album):
        tags = EasyMP3(file_name)
        tags["title"] = title
        tags["artist"] = artist
        tags["album"] = album
        tags.save()


def improve_name(song_name):
    """
    Improves file name by removing crap words
    """
    try:
        song_name = splitext(song_name)[0]
    except IndexError:
        pass

    song_name = song_name.partition('ft')[0]

    # Words to omit from song title for better results through spotify's API
    chars_filter = "()[]{}-:_/=+\"\'"
    words_filter = ('official', 'lyrics', 'audio', 'remixed', 'remix', 'video',
                    'full', 'version', 'music', 'mp3', 'hd', 'hq', 'uploaded', 'explicit')

    # Replace characters to filter with spaces
    song_name = ''.join(
        map(lambda c: " " if c in chars_filter else c, song_name))

    # Remove crap words
    song_name = re.sub('|'.join(re.escape(key) for key in words_filter),
                       "", song_name, flags=re.IGNORECASE)

    # Remove duplicate spaces
    song_name = re.sub(' +', ' ', song_name)

    return song_name.strip()


def img_search_google(album):
    """
    Search images using google 
    """

    album = album + " Album Art"
    url = ("https://www.google.com/search?q=" +
           quote(album.encode('utf-8')) + "&source=lnms&tbm=isch")
    header = {'User-Agent':
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/43.0.2357.134 Safari/537.36'
              }

    response = requests.get(url, headers=header)

    soup = BeautifulSoup(response.text, "html.parser")

    albumart_div = soup.find("div", {"class": "rg_meta"})
    albumart = json.loads(albumart_div.text)["ou"]

    return albumart
