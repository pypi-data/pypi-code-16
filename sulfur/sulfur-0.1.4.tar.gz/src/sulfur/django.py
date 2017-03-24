"""
Django-specific fixtures for Pytest
"""

import pytest

import sulfur

__all__ = ['client']


@pytest.fixture
def client():
    """
    A url checker integrated with Django.

    Usage::

        def test_basic_urls(db, user, client):
            url_list = [
                'users/',
                'users/{id}/',
                'users/{id}/edit',
            ]
            context = {'id': user.id}

            # Checks if all urls exist (return 200-OK) and are valid HTML5
            client.check_url(url_list, context, html5=True)
    """
    return sulfur.DjangoClient()
