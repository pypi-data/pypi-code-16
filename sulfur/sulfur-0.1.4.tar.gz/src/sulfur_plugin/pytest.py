""""
Sulfur py.test plugin.
"""
import os

import pytest

if not os.environ.get('SULFUR_DISABLE_PLUGIN', '').lower() == 'true':
    # We don't want to import sulfur globally in order to preserve coverage
    # stats for the sulfur package. If we import the sulfur module, parts of it will be
    # loaded before coverage starts its tracer, hence many lines will not be
    # counted when coverage runs.

    @pytest.fixture
    def driver(driver):
        import sulfur
        return sulfur.Driver()

    @pytest.fixture
    def client(driver):
        import sulfur.client
        return sulfur.Driver()

    @pytest.fixture
    def urlchecker():
        """
        Return the sulfur.urlchecker module.
        """

        import sulfur.urlchecker
        return sulfur.urlchecker
