from collections import namedtuple
from unittest.mock import MagicMock


def create_mock_object(class_):
    methods = fetch_methods(class_)
    mock_object = namedtuple('MockObject', methods)
    for method in methods:
        setattr(mock_object, method, MagicMock())
    return mock_object


def fetch_methods(class_):
    attributes = dir(class_)
    methods = filter(
        lambda attribute: _is_public_method(class_, attribute),
        attributes
    )
    return set(methods)


def _is_public_method(class_, attribute):
    return _is_function(class_, attribute) and _is_public(attribute)


def _is_function(class_, attribute):
    return callable(getattr(class_, attribute))


def _is_public(attribute):
    return not attribute.startswith('_')

