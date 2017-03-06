# -*- coding: utf-8 -*-

import mock
import pytest

import takumi_config


class MockConfig(dict):
    __getattr__ = dict.__getitem__

    def __init__(self):
        self.settings = {}

config = MockConfig()


@pytest.fixture
def mock_config():
    with mock.patch.object(takumi_config, 'config', config):
        yield config
        config.clear()
        config.settings.clear()
