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


def get_youtube_url(query):
    req = requests.get('https://www.googleapis.com/youtube/v3/search', params={
        'key': 'AIzaSyCMMllEgw9otcQPvsUSMY5tKmzVt_U4flQ',
        'part': 'snippet',
        'maxResults': 1,
        'q': query
    })
    response = req.json()
    try:
        video_id = response['items'][0]['id']['videoId']
        url = 'https://www.youtube.com/watch?v=' + video_id
        return url
    except KeyError:
        return False


def write_audio_tags(tags):
    af = eyed3.load(tags['file_name'])
    af.tag.artist = tags['artist']
    af.tag.album = tags['album']
    af.tag.title = tags['title']
    af.tag.track_num = tags['track_num']
    image = open(tags['image'], "rb").read()
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

        url = get_youtube_url(artist + ' - ' + track)

        if not url:
            continue

        clean_title = track.replace('/', '-')
        file_name = '%s.mp3' % clean_title

        cmd = 'youtube-dl -o "' + clean_title + '.%(ext)s" --extract-audio --audio-format mp3 ' + url
        call(cmd, shell=True)

        tags = {
            'file_name': file_name,
            'artist': artist,
            'title': track,
            'album': album_name,
            'track_num': tracks['track_number'],
            'image': image
        }
        write_audio_tags(tags)

    print('Done!')


if __name__ == '__main__':
    main()
