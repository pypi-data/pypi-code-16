from __future__ import print_function

import logging
logging.basicConfig(level=logging.DEBUG)

from oem import OemClient
from oem.media.show.identifier import EpisodeIdentifier
from oem_client_provider_release import IncrementalReleaseProvider
from oem_storage_codernitydb import CodernityDbStorage

import os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

log = logging.getLogger(__name__)


def run():
    # Initialize client
    client = OemClient(
        services=[
            'anidb'
        ],
        provider=IncrementalReleaseProvider(
            fmt='minimize+msgpack',
            storage=CodernityDbStorage(os.path.join(
                CURRENT_DIR,
                '.codernitydb',
                'anidb_incremental_github_example'
            ))
        )
    )

    #
    # AniDB -> TVDb: Basic
    #

    log.debug("\n%s\nAniDB -> TVDb: Basic\n%s", '=' * 60, '=' * 60)

    log.debug(client['anidb'].to('tvdb').map('3',    EpisodeIdentifier(1,  2)))
    log.debug(client['anidb'].to('tvdb').map('38',   EpisodeIdentifier(1,  2)))
    log.debug(client['anidb'].to('tvdb').map('818',  EpisodeIdentifier(0,  1)))
    log.debug(client['anidb'].to('tvdb').map('1041', EpisodeIdentifier(1, 45)))

    #
    # AniDB -> TVDb: Timeline
    #

    log.debug("\n%s\nAniDB -> TVDb: Timeline\n%s", '=' * 60, '=' * 60)

    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=34)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=49)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=50)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=51)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=64)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=99)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1, progress=100)))

    #
    # AniDB -> TMDb (Movie): Basic
    #

    log.debug("\n%s\nAniDB -> TMDb (Movie): Basic\n%s", '=' * 60, '=' * 60)

    log.debug(client['anidb'].to('tmdb:movie').map('83'))
    log.debug(client['anidb'].to('tmdb:movie').map('321'))
    log.debug(client['anidb'].to('tmdb:movie').map('399'))
    log.debug(client['anidb'].to('tmdb:movie').map('440'))

    #
    # Movies
    #

    log.debug("\n%s\nMovies\n%s", '=' * 60, '=' * 60)

    # AniDB -> IMDb
    log.debug(client['anidb'].to('imdb').get(       7103))

    # IMDb -> AniDB
    log.debug(client['imdb'].to('anidb').get("tt1663145"))

    #
    # Shows
    #

    log.debug("\n%s\nShows\n%s", '=' * 60, '=' * 60)

    # AniDB -> TVDb
    log.debug(client['anidb'].to('tvdb').get(     3))

    # TVDb -> AniDB
    log.debug(client['tvdb'].to('anidb').get( 70973))
    log.debug(client['tvdb'].to('anidb').get( 71551))
    log.debug(client['tvdb'].to('anidb').get(103691))
    log.debug(client['tvdb'].to('anidb').get(136251))
    log.debug(client['tvdb'].to('anidb').get(137151))
    log.debug(client['tvdb'].to('anidb').get(138691))


if __name__ == '__main__':
    # Run example
    run()

    # Display call statistics
    from oem_framework.core.elapsed import Elapsed

    for line in Elapsed.format_statistics():
        print(line)
