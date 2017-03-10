# -*- coding: utf-8 -*-

import pytest
import mock
import os


TESTS_DIR = os.path.join(os.path.dirname(__file__), 'app.yaml')


@pytest.fixture(autouse=True)
def config_path():
    with mock.patch.dict(os.environ, {'TAKUMI_APP_CONFIG_PATH': TESTS_DIR}):
        yield
