import mock

from schematics.models import Model


class SampleModel(Model):
    pass


def test_equality_against_mock_any():
    assert SampleModel() == mock.ANY
