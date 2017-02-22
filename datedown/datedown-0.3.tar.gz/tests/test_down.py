# The MIT License (MIT)
#
# Copyright (c) 2016,Christoph Paulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''
Tests for downloading.
'''
import os
import shutil
from datedown.down import download
from datedown.down import check_downloaded
import pytest


@pytest.fixture
def targets(request):
    curpath = os.path.split(os.path.abspath(__file__))[0]
    targets = [os.path.join(curpath, "L8", "233", "081", "LC82330812015124LGN00", "LC82330812015124LGN00_MTL.txt"),
               os.path.join(curpath, "L8", "139", "045", "LC81390452014295LGN00", "LC81390452014295LGN00_MTL.txt")]

    def cleanup():
        shutil.rmtree(os.path.join(curpath, "L8"))

    try:
        cleanup()
    except OSError:
        pass

    request.addfinalizer(cleanup)

    return targets


def test_download(targets):
    """
    Test simple download of two files.
    This library is not really made for Landsat style data but
    this is hosted somewhat reliably by Amazon and it has a small text
    file that can be downloaded quickly.
    """
    urls = ["https://s3-us-west-2.amazonaws.com/landsat-pds/L8/233/081/LC82330812015124LGN00/LC82330812015124LGN00_MTL.txt",
            "http://landsat-pds.s3.amazonaws.com/L8/139/045/LC81390452014295LGN00/LC81390452014295LGN00_MTL.txt"]

    download(urls, targets)
    not_urls, not_fnames = check_downloaded(urls, targets)
    assert len(not_urls) == 0
    assert len(not_fnames) == 0
