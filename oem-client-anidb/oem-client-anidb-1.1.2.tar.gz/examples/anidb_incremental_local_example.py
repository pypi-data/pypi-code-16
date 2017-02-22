from __future__ import print_function

import logging
logging.basicConfig(level=logging.DEBUG)

from oem import OemClient
from oem.media.show.identifier import EpisodeIdentifier
from oem_client_provider_release import IncrementalReleaseProvider
from oem_storage_codernitydb import CodernityDbStorage
from semantic_version import Version

import os

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

log = logging.getLogger(__name__)


class DemoReleaseProvider(IncrementalReleaseProvider):
    def get_available_version(self, source, target):
        return Version('1.16.1')


def run():
    # Initialize client
    client = OemClient(
        services=[
            'anidb'
        ],
        provider=DemoReleaseProvider(
            database_url='http://127.0.0.1:5000/',
            fmt='minimize+msgpack',
            storage=CodernityDbStorage(os.path.join(
                CURRENT_DIR,
                '.codernitydb',
                'anidb_incremental_local_example'
            ))
        )
    )

    #
    # Basic
    #

    log.debug("\n%s\nBasic\n%s", '=' * 60, '=' * 60)
    log.debug(client['anidb'].to('tvdb').map('3',    EpisodeIdentifier(1,  2)))
    log.debug(client['anidb'].to('tvdb').map('38',   EpisodeIdentifier(1,  2)))
    log.debug(client['anidb'].to('tvdb').map('818',  EpisodeIdentifier(0,  1)))
    log.debug(client['anidb'].to('tvdb').map('1041', EpisodeIdentifier(1, 45)))

    #
    # Timeline
    #

    log.debug("\n%s\nTimeline\n%s", '=' * 60, '=' * 60)
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=34)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=49)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=50)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=51)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=64)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1,  progress=99)))
    log.debug(client['anidb'].to('tvdb').map('10648', EpisodeIdentifier(1, 1, progress=100)))

    # Movies
    log.debug("\n%s\nMovies\n%s", '=' * 60, '=' * 60)
    log.debug(client['anidb'].to('imdb').get(       7103))
    log.debug(client['imdb'].to('anidb').get("tt1663145"))

    # Shows
    log.debug("\n%s\nShows\n%s", '=' * 60, '=' * 60)
    log.debug(client['anidb'].to('tvdb').get(     3))
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
