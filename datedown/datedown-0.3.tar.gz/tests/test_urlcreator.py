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
Tests for urlcreator
'''
from datetime import datetime
from datedown.urlcreator import create_dt_url


def test_create_dt_url_no_dt():

    url_should = "http://example.com/sub1/sub2/filename.nc"
    url = create_dt_url(datetime(2000, 1, 1),
                        "http://example.com",
                        "filename.nc",
                        subdirs=["sub1", "sub2"])
    assert url == url_should


def test_create_dt_url_fname_dt():

    url_should = "http://example.com/sub1/sub2/file20000101name.nc"
    url = create_dt_url(datetime(2000, 1, 1),
                        "http://example.com",
                        "file%Y%m%dname.nc",
                        subdirs=["sub1", "sub2"])
    assert url == url_should


def test_create_dt_url_subdir_dt():

    url_should = "http://example.com/2000/01/file20000101name.nc"
    url = create_dt_url(datetime(2000, 1, 1),
                        "http://example.com",
                        "file%Y%m%dname.nc",
                        subdirs=["%Y", "%m"])
    assert url == url_should
