import os
import aipfs
import pytest
from asynctest import CoroutineMock


dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def client(request):
    mock = CoroutineMock
    mock.request = CoroutineMock()
    ipfs = aipfs.IPFS(transport=mock).__enter__()

    def teardown():
        ipfs.__exit__()

    request.addfinalizer(teardown)

    return ipfs


@pytest.fixture()
def dummyfilestream(request):
    file = open(dir_path + "/dummy_file")

    def teardown():
        file.close()

    request.addfinalizer(teardown)

    return file
