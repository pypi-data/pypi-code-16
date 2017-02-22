from oem import AbsoluteNumberRequiredError
from oem.media.movie import MovieIdentifier
from oem.media.show import EpisodeIdentifier, EpisodeMatch
from oem_framework.models import EpisodeMapping
from oem_framework.models import Range

from tests.fixtures import client
import pytest


#
# Matches
#


def test_matches_anidb_episode(client):
    assert client['tvdb'].to('anidb').map('72025', EpisodeIdentifier(4, 12)) == EpisodeMatch({'anidb': '2673'}, 1, 12)
    assert client['tvdb'].to('anidb').map('72025', EpisodeIdentifier(5, 25)) is None

    assert client['tvdb'].to('anidb').map('76703', EpisodeIdentifier(15, 20)) == EpisodeMatch({'anidb': '9216'}, 1, 20)
    assert client['tvdb'].to('anidb').map('76703', EpisodeIdentifier(15, 39)) == EpisodeMatch({'anidb': '9764'}, 1, 1)
    assert client['tvdb'].to('anidb').map('76703', EpisodeIdentifier(15, 40)) == EpisodeMatch({'anidb': '9764'}, 1, 2)

    assert client['tvdb'].to('anidb').map('157211', EpisodeIdentifier(2, 10)) == EpisodeMatch({'anidb': '1703'}, 1, 36)


def test_matches_anidb_episode_absolute(client):
    assert client['tvdb'].to('anidb').map('76703', EpisodeIdentifier(1,  1,   1)) == EpisodeMatch({'anidb': '230'}, absolute_num=1)
    assert client['tvdb'].to('anidb').map('76703', EpisodeIdentifier(1, 82,  82)) == EpisodeMatch({'anidb': '230'}, absolute_num=82)
    assert client['tvdb'].to('anidb').map('76703', EpisodeIdentifier(3,  4, 122)) == EpisodeMatch({'anidb': '230'}, absolute_num=122)


def test_matches_anidb_episode_timeline(client):
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 1, progress=3.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=1.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 1, progress=49.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=24.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 1, progress=53.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=26.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 1, progress=99.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=49.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 1, progress=100.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=50.0)

    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 2, progress=3.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=51.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 2, progress=49.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=74.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 2, progress=53.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=76.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 2, progress=99.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=99.5)
    assert client['tvdb'].to('anidb').map('232511', EpisodeIdentifier(1, 2, progress=100.0)) == EpisodeMatch({'anidb': '1491'}, 1, 1, progress=100.0)


def test_matches_tvdb_movie(client):
    assert client['anidb'].to('tvdb').map('2221') == EpisodeMatch({'tvdb': '112641'}, 0, 2)


def test_matches_tvdb_episode(client):
    assert client['anidb'].to('tvdb').map('1', EpisodeIdentifier(1, 1)) == EpisodeMatch({'tvdb': '72025'}, 1, 1)

    assert client['anidb'].to('tvdb').map('4', EpisodeIdentifier(1, 1)) == EpisodeMatch({'tvdb': '72025'}, 2, 1)

    assert client['anidb'].to('tvdb').map('202', EpisodeIdentifier(1, 1)) == EpisodeMatch({'tvdb': '70350'}, 0, 2)
    assert client['anidb'].to('tvdb').map('202', EpisodeIdentifier(1, 2)) == EpisodeMatch({'tvdb': '70350'}, 0, 2)

    assert client['anidb'].to('tvdb').map('1041', EpisodeIdentifier(1,  1)) == EpisodeMatch({'tvdb': '76703'}, 1, 1)
    assert client['anidb'].to('tvdb').map('1041', EpisodeIdentifier(1, 41)) == EpisodeMatch({'tvdb': '76703'}, 7, 1)

    assert client['anidb'].to('tvdb').map('1045', EpisodeIdentifier(1, 1)) == EpisodeMatch({'tvdb': '81472'}, 0, 5)

    assert client['anidb'].to('tvdb').map('5101', EpisodeIdentifier(0, 2)) == EpisodeMatch({'tvdb': '80644'}, 0, 2)
    assert client['anidb'].to('tvdb').map('5101', EpisodeIdentifier(1, 2)) == EpisodeMatch({'tvdb': '80644'}, 1, 2)
    assert client['anidb'].to('tvdb').map('5101', EpisodeIdentifier(2, 2)) == EpisodeMatch({'tvdb': '80644'}, 2, 2)


def test_matches_tvdb_episode_absolute(client):
    assert client['anidb'].to('tvdb').map('230', EpisodeIdentifier(2, 52, 52)) == EpisodeMatch({'tvdb': '76703'}, absolute_num=52)


def test_matches_tvdb_episode_progress(client):
    assert client['anidb'].to('tvdb').map('5101', EpisodeIdentifier(1, 2, progress=59.5)) == EpisodeMatch({'tvdb': '80644'}, 1, 2, progress=59.5)


def test_matches_tvdb_movie_progress(client):
    assert client['anidb'].to('tvdb').map('2221', MovieIdentifier(progress=49)) == EpisodeMatch({'tvdb': '112641'}, 0, 2, progress=49)


def test_matches_tvdb_episode_timeline(client):
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=1.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 1, progress=3.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=24.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 1, progress=49.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=26.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 1, progress=53.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=49.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 1, progress=99.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=50.0)) == EpisodeMatch({'tvdb': '232511'}, 1, 1, progress=100.0)

    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=51.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 2, progress=3.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=74.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 2, progress=49.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=76.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 2, progress=53.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=99.5)) == EpisodeMatch({'tvdb': '232511'}, 1, 2, progress=99.0)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, progress=100.0)) == EpisodeMatch({'tvdb': '232511'}, 1, 2, progress=100.0)


def test_matches_tvdb_episode_mappings(client):
    assert client['anidb'].to('tvdb').map(
        '1491', EpisodeIdentifier(1, 1, progress=1.5),
        resolve_mappings=False
    ) == EpisodeMatch(
        {'tvdb': '232511'},
        mappings=[
            EpisodeMapping(None, None, '1', '1', {'source': Range(None,  0,  50)}),
            EpisodeMapping(None, None, '1', '2', {'source': Range(None, 50, 100)})
        ]
    )


def test_matches_tvdb_episode_part(client):
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, part=1)) == EpisodeMatch({'tvdb': '232511'}, 1, 1, part=1)
    assert client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1, part=2)) == EpisodeMatch({'tvdb': '232511'}, 1, 2, part=2)


#
# Invalid / Missing
#


def test_absolute_number_required(client):
    with pytest.raises(AbsoluteNumberRequiredError):
        client['anidb'].to('tvdb').map('230', EpisodeIdentifier(2, 52))


def test_invalid_identifier(client):
    with pytest.raises(ValueError):
        client['anidb'].to('tvdb').map('202', EpisodeIdentifier(None, None))

    with pytest.raises(ValueError):
        client['anidb'].to('tvdb').map('202', EpisodeIdentifier(1, None))


def test_invalid_timeline(client):
    with pytest.raises(ValueError):
        client['anidb'].to('tvdb').map('1491', EpisodeIdentifier(1, 1))


def test_missing_item(client):
    assert client['anidb'].to('tvdb').map('missing', EpisodeIdentifier(1, 1)) is None


def test_missing_default_season(client):
    assert client['anidb'].to('tvdb').map('no_default_season', EpisodeIdentifier(1, 1)) is None
