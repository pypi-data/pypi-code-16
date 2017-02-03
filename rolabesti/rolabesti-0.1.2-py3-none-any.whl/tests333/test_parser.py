# -*- coding: utf-8 -*-

from rolabesti.parser import parse


def test_parse_with_valid_trackpaths():
    place = 'some place'
    genre = 'some genre'
    album = 'some album'
    artist = 'some artist'
    side = 'some side'
    filename = 'some filename'

    trackpath = '/path/to/music/directory/Places/{}/Genres/{}/Albums/{}/{}.mp3'.format(place, genre, album, filename)
    track = parse(trackpath)
    assert type(track) == dict and len(track) == 4
    assert track['place'] == place and track['genre'] == genre and track['album'] == album

    trackpath = '/path/to/music/directory/Places/{}/Genres/{}/Albums/{}/{}/{}.mp3'.format(place, genre, album, side, filename)
    track = parse(trackpath)
    assert type(track) == dict and len(track) == 5
    assert track['place'] == place and track['genre'] == genre and track['album'] == album and track['side'] == side
