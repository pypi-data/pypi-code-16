# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import pytest

from path2css import request_path_to_css_names


def test_request_path_to_css_names_raises_warning():
    pytest.deprecated_call(request_path_to_css_names, item="a/b/c/d")
