import pytest
import miniserver


def test_project_defines_author_and_version():
    assert hasattr(miniserver, '__author__')
    assert hasattr(miniserver, '__version__')
