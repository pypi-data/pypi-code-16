import pytest

from files_by_date.service.files_service import FilesService


def test_files_service_instance_raises():
    with pytest.raises(NotImplementedError):
        FilesService()
