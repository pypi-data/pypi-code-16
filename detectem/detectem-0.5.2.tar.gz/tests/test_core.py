import pytest

from detectem.core import Detector
from detectem.plugin import Plugin


class TestDetector():
    HAR_ENTRY_1 = {
        'request': {
            'url': 'http://domain.tld/libA-1.4.2.js'
        },
        'response': {
            'url': 'http://domain.tld/libA-1.4.2.js'
        },
    }

    def test_detector_starts_with_empty_results(self):
        d = Detector({'har': None, 'softwares': None}, [], None)
        assert not d._results

    def test_get_version_from_url_without_matcher(self):
        class TPlugin(Plugin):
            matchers = []
        pass


