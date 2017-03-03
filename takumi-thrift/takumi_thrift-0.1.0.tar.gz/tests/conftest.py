# -*- coding: utf-8 -*-

import mock
import pytest


@pytest.fixture
def proto():
    p = mock.Mock()
    yield p
