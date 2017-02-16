# Copyright (C) 2016 Red Hat
#
# This file is part of fedfind.
#
# fedfind is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: Adam Williamson <awilliam@redhat.com>

"""Test configuration and fixtures."""

from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest
import shutil
import subprocess
import time

import mock

import fedfind.const

def pytest_addoption(parser):
    parser.addoption("--nocaplog", action="store_true",
        help="Skip tests using the caplog fixture")

@pytest.yield_fixture(scope="session")
def http():
    """Run a SimpleHTTPServer that we can use as a fake dl.fp.o. Serve
    the contents of tests/data/http, for the entire test session. We
    just do this with subprocess as we need it to run parallel to the
    tests and this is really the easiest way.
    """
    root = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'data', 'http')
    # Always use python2 for this (for now)
    args = ("python2", "-m", "SimpleHTTPServer", "5001")
    proc = subprocess.Popen(args, cwd=root)
    # this is rather ugly, but if we yield immediately, the tests will
    # try to use the server before it's actually started up. I don't
    # know of a way to wait for the sub-process to print a specific
    # message but *not* wait for it to complete (communicate() waits
    # for completion), so just wait a second.
    time.sleep(1)
    # Redefine the HTTPS_DL constant to point to the fake server
    fedfind.const.HTTPS_DL = 'http://localhost:5001/pub'
    # yield to the tests
    yield None
    # this is the teardown: kill the server
    proc.kill()

@pytest.yield_fixture(scope="function")
def clean_home():
    """Provides a fake user home directory, at data/home/ under the
    tests directory. Before the test, re-create it and patch
    os.path.expanduser to return it. After the test, delete it. Yields
    the full path.
    """
    home = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'home')
    if os.path.exists(home):
        shutil.rmtree(home)
    os.makedirs(home)
    patcher = mock.patch('os.path.expanduser', return_value=home)
    patcher.start()
    yield home
    # teardown
    patcher.stop()
    if os.path.exists(home):
        shutil.rmtree(home)
