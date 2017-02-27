import requests
import spotipy
import os
import urllib
from subprocess import call
from mutagen.easyid3 import EasyID3
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("album_id", help='The Spotify ID for the album.')
    args = parser.parse_args()

    urn = 'spotify:album:' + args.album_id
    sp = spotipy.Spotify()
    album = sp.album(urn)
    album_name = album['name']
    image_url = album['images'][0]['url']
    print('Downloading ' + album_name)

    try:
        os.mkdir(album_name)
    except OSError:
        print('Directory already exists. Continuing..')

    os.chdir(album_name)
    file_name = album_name + '.jpg'
    urllib.urlretrieve(image_url, file_name)

    for tracks in album['tracks']['items']:
        artist = tracks['artists'][0]['name']
        track = tracks['name']
        query = artist + ' - ' + track
        params = {
            'key': os.environ['YOUTUBE_API_KEY'],
            'part': 'snippet',
            'maxResults': 1,
            'q': query
        }
        req = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
        data = req.json()
        try:
            video_id = data['items'][0]['id']['videoId']
        except KeyError:
            continue
        url = 'https://www.youtube.com/watch?v=' + video_id
        cmd = 'youtube-dl -o "' + query + '.%(ext)s" --extract-audio --audio-format mp3 ' + url
        call(cmd, shell=True)
        audio = EasyID3(query + '.mp3')
        audio['title'] = track
        audio['artist'] = artist
        audio['album'] = album_name
        audio.save()

    print('Done!')


if __name__ == '__main__':
    main()
