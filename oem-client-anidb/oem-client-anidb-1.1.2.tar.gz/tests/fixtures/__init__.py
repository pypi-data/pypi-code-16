from oem import Client
from oem_client_provider_package import PackageProvider

import logging
import os
import pytest

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)


@pytest.fixture(scope="module")
def client():
    try:
        client = Client(
            services=[
                'anidb'
            ],
            provider=PackageProvider(
                search_paths=[
                    os.path.join(BASE_DIR)
                ],
                use_installed_packages=False
            )
        )
    except Exception as ex:
        log.warn('Unable to construct client - %s', ex, exc_info=True)
        return None

    if not client:
        log.warn('Unable to construct client')
        return None

    client.load_all()
    return client
