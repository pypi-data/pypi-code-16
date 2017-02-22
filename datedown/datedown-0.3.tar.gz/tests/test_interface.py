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
Tests for the interface including.

We host the test_data directory during the test.
'''

from datetime import datetime
from functools import partial
import sys
import os
import shutil

from datedown.urlcreator import create_dt_url
from datedown.fname_creator import create_dt_fpath
from datedown.interface import download_by_dt
from datedown.interface import n_hours
from datedown.interface import parse_args
from datedown.interface import main
from datedown.interface import main_recursive
from datedown.down import download

from subprocess import Popen
import pytest


@pytest.fixture
def temp_http_server(request):
    pdir = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    modules = {2: "SimpleHTTPServer",
               3: "http.server"}
    p = Popen(["python", "-m", modules[sys.version_info.major], "8888"])
    os.chdir(pdir)

    def func():
        p.terminate()
    request.addfinalizer(func)


@pytest.fixture
def output_path(request):

    output_path = os.path.join(os.path.dirname(__file__), "output")

    def cleanup():
        shutil.rmtree(output_path)

    try:
        cleanup()
    except OSError:
        pass

    request.addfinalizer(cleanup)

    return output_path


def test_interface(output_path, temp_http_server):
    dts = [datetime(2000, 1, 1),
           datetime(2000, 1, 2),
           datetime(2000, 2, 1)]
    fname = "file_%Y_%m_%d.txt"
    subdirs = ["test_data",
               "year_month_subfolders",
               '%Y', '%m']
    url_create_fn = partial(create_dt_url, root="http://localhost:8888",
                            fname=fname, subdirs=subdirs)
    fname_create_fn = partial(create_dt_fpath, root=output_path,
                              fname=fname)
    download_by_dt(dts, url_create_fn,
                   fname_create_fn, download)

    fnames_should = map(fname_create_fn, dts)
    for fname_should in fnames_should:
        assert os.path.exists(fname_should)


def test_n_hours():
    st = "6H"
    assert 6 == n_hours(st)
    st = "6h"
    assert 6 == n_hours(st)
    st = "8H"
    assert 8 == n_hours(st)
    st = "18H"
    assert 18 == n_hours(st)
    st = "2D"
    assert 48 == n_hours(st)
    st = "2d"
    assert 48 == n_hours(st)
    st = "1D"
    assert 24 == n_hours(st)


def test_parse_args():
    args = ["2007-01-01", "2007-01-10T10:11",
            "http://localhost:8888",
            "file.txt",
            "/root/files",
            "--urlsubdirs", "%Y", "%m",
            "--localfname=local.txt",
            "--localsubdirs", "%m", "%d",
            "--interval=5H",
            "--username=test",
            "--password=test",
            "--n_proc=4"]
    a = parse_args(args)
    assert a.start == datetime(2007, 1, 1)
    assert a.end == datetime(2007, 1, 10, 10, 11)
    assert a.urlroot == "http://localhost:8888"
    assert a.urlfname == "file.txt"
    assert a.localroot == "/root/files"
    assert a.urlsubdirs == ['%Y', '%m']
    assert a.localfname == 'local.txt'
    assert a.localsubdirs == ['%m', '%d']
    assert a.interval == 5
    assert a.username == "test"
    assert a.password == "test"
    assert a.n_proc == 4


def test_parse_args_single_subdirs():
    args = ["2007-01-01", "2007-01-10T10:11",
            "http://localhost:8888",
            "file.txt",
            "/root/files",
            "--urlsubdirs", "%Y",
            "--localfname=local.txt",
            "--localsubdirs", "%m",
            "--interval=5H"]
    a = parse_args(args)
    assert a.start == datetime(2007, 1, 1)
    assert a.end == datetime(2007, 1, 10, 10, 11)
    assert a.urlroot == "http://localhost:8888"
    assert a.urlfname == "file.txt"
    assert a.localroot == "/root/files"
    assert a.urlsubdirs == ['%Y']
    assert a.localfname == 'local.txt'
    assert a.localsubdirs == ['%m']
    assert a.interval == 5
    assert a.n_proc == 1
    assert a.username == None
    assert a.password == None


def test_parse_args_defaults():
    args = ["2007-01-01", "2007-01-10T10:11",
            "http://localhost:8888",
            "file.txt",
            "/root/files",
            "--urlsubdirs", "%Y"]
    a = parse_args(args)
    assert a.start == datetime(2007, 1, 1)
    assert a.end == datetime(2007, 1, 10, 10, 11)
    assert a.urlroot == "http://localhost:8888"
    assert a.urlfname == "file.txt"
    assert a.localroot == "/root/files"
    assert a.urlsubdirs == ['%Y']
    assert a.localfname == 'file.txt'
    assert a.localsubdirs == ['%Y']
    assert a.interval == 24
    assert a.n_proc == 1
    assert a.username == None
    assert a.password == None


def test_main(output_path, temp_http_server):
    args = ["2000-01-01", "2000-01-02",
            "http://localhost:8888",
            "file_%Y_%m_%d.txt",
            output_path,
            "--urlsubdirs", "test_data", "year_month_subfolders", '%Y', '%m']

    main(args)

    fnames_should = [os.path.join(output_path, "test_data",
                                  "year_month_subfolders", '2000', '01',
                                  'file_2000_01_01.txt'),
                     os.path.join(output_path, "test_data",
                                  "year_month_subfolders", '2000', '01',
                                  'file_2000_01_02.txt')]
    for fname_should in fnames_should:
        assert os.path.exists(fname_should)


def test_main_recursive(output_path, temp_http_server):
    args = ["2000-01-01", "2000-01-02",
            "http://localhost:8888",
            output_path,
            "--urlsubdirs", "test_data", "year_month_subfolders", '%Y', '%m']

    main_recursive(args)

    fnames_should = [os.path.join(output_path, "test_data",
                                  "year_month_subfolders", '2000', '01',
                                  'file_2000_01_01.txt'),
                     os.path.join(output_path, "test_data",
                                  "year_month_subfolders", '2000', '01',
                                  'file_2000_01_02.txt')]
    for fname_should in fnames_should:
        assert os.path.exists(fname_should)
