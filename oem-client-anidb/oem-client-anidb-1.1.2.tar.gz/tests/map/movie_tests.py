from oem.media.movie import MovieIdentifier, MovieMatch
from oem.media.show import EpisodeIdentifier

from tests.fixtures import client
import pytest


#
# Matches
#


def test_matches_anidb_movie(client):
    assert client['tmdb:movie'].to('anidb').map('823') == MovieMatch({'anidb': '83'})
    assert client['tmdb:movie'].to('anidb').map('16990') == MovieMatch({'anidb': '321'})
    assert client['tmdb:movie'].to('anidb').map('18837') == MovieMatch({'anidb': '3392'})
    assert client['tmdb:movie'].to('anidb').map('25446') == MovieMatch({'anidb': '7183'})


def test_matches_imdb_episode(client):
    assert client['anidb'].to('imdb').map('1045', EpisodeIdentifier(1, 1)) == MovieMatch({'imdb': 'tt1125254'})


def test_matches_imdb_episode_part(client):
    assert client['anidb'].to('imdb').map('7439', EpisodeIdentifier(1, 1)) == MovieMatch({'imdb': 'tt1754177'})
    assert client['anidb'].to('imdb').map('7439', EpisodeIdentifier(1, 2)) == MovieMatch({'imdb': 'tt2231375'})


def test_matches_imdb_episode_progress(client):
    assert client['anidb'].to('imdb').map('1045', EpisodeIdentifier(1, 1, progress=49)) == MovieMatch({'imdb': 'tt1125254'}, progress=49)

    assert client['anidb'].to('imdb').map('7439', EpisodeIdentifier(1, 1, progress=49)) == MovieMatch({'imdb': 'tt1754177'}, progress=49)
    assert client['anidb'].to('imdb').map('7439', EpisodeIdentifier(1, 2, progress=64)) == MovieMatch({'imdb': 'tt2231375'}, progress=64)


def test_matches_imdb_movie(client):
    assert client['anidb'].to('imdb').map('1043', MovieIdentifier()) == MovieMatch({'imdb': 'tt0142235'})
    assert client['anidb'].to('imdb').map('1045') == MovieMatch({'imdb': 'tt1125254'})


def test_matches_imdb_movie_part(client):
    assert client['anidb'].to('imdb').map('7439', MovieIdentifier(part=1)) == MovieMatch({'imdb': 'tt1754177'})
    assert client['anidb'].to('imdb').map('7439', MovieIdentifier(part=2)) == MovieMatch({'imdb': 'tt2231375'})


def test_matches_imdb_movie_progress(client):
    assert client['anidb'].to('imdb').map('1043', MovieIdentifier(progress=49)) == MovieMatch({'imdb': 'tt0142235'}, progress=49)

    assert client['anidb'].to('imdb').map('7439', MovieIdentifier(part=1, progress=49)) == MovieMatch({'imdb': 'tt1754177'}, progress=49)
    assert client['anidb'].to('imdb').map('7439', MovieIdentifier(part=2, progress=64)) == MovieMatch({'imdb': 'tt2231375'}, progress=64)


def test_matches_tmdb_movie(client):
    assert client['anidb'].to('tmdb:movie').map('83') == MovieMatch({'tmdb:movie': '823'})
    assert client['anidb'].to('tmdb:movie').map('321') == MovieMatch({'tmdb:movie': '16990'})
    assert client['anidb'].to('tmdb:movie').map('399') == MovieMatch({'tmdb:movie': '77192'})
    assert client['anidb'].to('tmdb:movie').map('440') == MovieMatch({'tmdb:movie': '41421'})



#
# Invalid / Missing
#


def test_invalid_identifier(client):
    assert client['anidb'].to('imdb').map('1045', EpisodeIdentifier(1, 2)) is None
