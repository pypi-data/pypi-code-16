import requests
import spotipy
import os
import urllib
from subprocess import call
import eyed3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("album_id", help='The Spotify ID for the album.')
args = parser.parse_args()


def write_audio_tags(params):
    af = eyed3.load(params['file_name'])
    af.tag.artist = params['artist']
    af.tag.album = params['album']
    af.tag.title = params['title']
    af.tag.track_num = params['track_num']
    image = open(params['image'], "rb").read()
    af.tag.images.set(3, image, "image/jpeg")
    af.tag.save()


def main():
    urn = 'spotify:album:' + args.album_id
    sp = spotipy.Spotify()
    album = sp.album(urn)
    album_name = album['name']

    print('Downloading ' + album_name)

    try:
        os.mkdir(album_name)
    except OSError:
        print('Directory already exists. Continuing..')

    os.chdir(album_name)
    image = album_name + '.jpg'
    image_url = album['images'][0]['url']
    urllib.urlretrieve(image_url, image)

    for tracks in album['tracks']['items']:

        artist = tracks['artists'][0]['name']
        track = tracks['name']
        query = artist + ' - ' + track
        file_name = query + '.mp3'
        
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

        write_audio_tags(params={
            'file_name': file_name,
            'artist': artist,
            'title': track,
            'album': album_name,
            'track_num': tracks['track_number'],
            'image': image
        })
        
    print('Done!')


if __name__ == '__main__':
    main()
