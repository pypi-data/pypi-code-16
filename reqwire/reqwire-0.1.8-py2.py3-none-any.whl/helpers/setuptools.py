"""Setuptools integrations."""
from __future__ import absolute_import


def discover_requirements_keyword(dist, keyword, value):
    print(dist)
    print(dist.metadata)
