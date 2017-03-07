from __future__ import absolute_import, division, print_function

from oem.core.exceptions import AbsoluteNumberRequiredError
from oem.media.show import ShowMapper, EpisodeIdentifier
from oem_core.models import Collection, Show, Season, Episode, EpisodeMapping
from tests.core.mock import MockService

import pytest

collection = Collection(None, 'anidb', 'tvdb')
service = MockService('anidb', 'tvdb')


#
# Show
#


def test_show_invalid_default_season():
    mapper = ShowMapper(service)

    assert mapper.match(
        Show(collection, {}, [], default_season='INVALID'),
        EpisodeIdentifier(1, 1)
    ) is None


#
# Season
#


def test_season_absolute_number_required():
    mapper = ShowMapper(service)

    show = Show(collection, {}, [])
    show.seasons['a'] = Season(collection, show, 'a')

    with pytest.raises(AbsoluteNumberRequiredError):
        mapper.match(show, EpisodeIdentifier(1, 1))


def test_season_invalid_default_season():
    mapper = ShowMapper(service)

    show = Show(collection, {}, [])
    show.seasons['1'] = Season(collection, show, '1', default_season='INVALID')

    assert mapper.match(show, EpisodeIdentifier(1, 1)) is None


def test_season_invalid_match():
    mapper = ShowMapper(service)

    show = Show(collection, {}, [])
    show.seasons['1'] = Season(collection, show, '1')

    assert mapper.match(show, EpisodeIdentifier(1, 1)) is None


#
# Episode
#


def test_episode_invalid_mapping_season():
    mapper = ShowMapper(service)

    show = Show(collection, {}, [])
    show.seasons['1'] = Season(collection, show, '1')
    show.seasons['1'].episodes['1'] = Episode(collection, show.seasons['1'], '1')
    show.seasons['1'].episodes['1'].mappings = [
        EpisodeMapping(collection, show.seasons['1'].episodes['1'], 'INVALID', '1')
    ]

    assert mapper.match(show, EpisodeIdentifier(1, 1)) is None


def test_episode_invalid_mapping_episode():
    mapper = ShowMapper(service)

    show = Show(collection, {}, [])
    show.seasons['1'] = Season(collection, show, '1')
    show.seasons['1'].episodes['1'] = Episode(collection, show.seasons['1'], '1')
    show.seasons['1'].episodes['1'].mappings = [
        EpisodeMapping(collection, show.seasons['1'].episodes['1'], '1', 'INVALID')
    ]

    assert mapper.match(show, EpisodeIdentifier(1, 1)) is None


def test_episode_invalid_match():
    mapper = ShowMapper(service)

    show = Show(collection, {}, [])
    show.seasons['1'] = Season(collection, show, '1')
    show.seasons['1'].episodes['1'] = Episode(collection, show.seasons['1'], '1')
    show.seasons['1'].episodes['1'].mappings = [
        EpisodeMapping(collection, show.seasons['1'].episodes['1'], '1', '1')
    ]

    assert mapper.match(show, EpisodeIdentifier(1, 1)) is None
