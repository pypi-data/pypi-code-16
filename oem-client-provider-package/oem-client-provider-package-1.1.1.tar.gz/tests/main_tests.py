from oem import Client
from oem_client_provider_package import PackageProvider

client = Client([], PackageProvider())
provider = client.provider


def test_parse_database_name_basic():
    # imdb
    assert provider._parse_database_name(
        'oem_database_anidb_imdb',
        [('anidb', 'imdb')]
    ) == (
        'anidb', 'imdb',
        None
    )

    # tvdb
    assert provider._parse_database_name(
        'oem_database_anidb_tvdb',
        [('anidb', 'tvdb')]
    ) == (
        'anidb', 'tvdb',
        None
    )


def test_parse_database_name_formats():
    # json
    assert provider._parse_database_name(
        'oem_database_anidb_tvdb_json',
        [('anidb', 'tvdb')]
    ) == (
        'anidb', 'tvdb',
        'json'
    )

    # pre.json
    assert provider._parse_database_name(
        'oem_database_anidb_tvdb_pre_json',
        [('anidb', 'tvdb')]
    ) == (
        'anidb', 'tvdb',
        'pre_json'
    )


def test_parse_database_name_extended():
    # tmdb:movie
    assert provider._parse_database_name(
        'oem_database_anidb_tmdb_movie',
        [('anidb', 'tmdb:movie')]
    ) == (
        'anidb', 'tmdb:movie',
        None
    )

    # tmdb:show
    assert provider._parse_database_name(
        'oem_database_anidb_tmdb_show',
        [('anidb', 'tmdb:show')]
    ) == (
        'anidb', 'tmdb:show',
        None
    )


def test_parse_database_name_extended_formats():
    # tmdb:movie, json
    assert provider._parse_database_name(
        'oem_database_anidb_tmdb_movie_json',
        [('anidb', 'tmdb:movie')]
    ) == (
        'anidb', 'tmdb:movie',
        'json'
    )

    # tmdb:show, pre.json
    assert provider._parse_database_name(
        'oem_database_anidb_tmdb_movie_pre_json',
        [('anidb', 'tmdb:movie')]
    ) == (
        'anidb', 'tmdb:movie',
        'pre_json'
    )
