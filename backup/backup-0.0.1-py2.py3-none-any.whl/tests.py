import shutil
import unittest.mock as mock

from . import arc_pack, arc_unpack


@mock.patch("shutil.make_archive")
def test_arc_pack_calls_make_archive(mocked_make_archive):
    arc_pack('t1', 't2')
    shutil.make_archive.assert_called()


@mock.patch("shutil.make_archive")
def test_arc_pack_fails_gracefully(mocked_make_archive):
    shutil.make_archive.side_effect = OSError('File(s) not available!')

    assert arc_pack('t1', 't2') is False


@mock.patch("shutil.unpack_archive")
def test_arc_unpack_calls_unpack_archive(mocked_unpack_archive):
    arc_unpack('t1')
    shutil.unpack_archive.assert_called()
