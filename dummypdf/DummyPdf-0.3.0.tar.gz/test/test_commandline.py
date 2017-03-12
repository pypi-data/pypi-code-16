# Copyright 2017 Louis Paternault
#
# This program is free software: you can redistribute it and/or modify
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

"""Tests"""

import os
import subprocess
import sys
import unittest

from wand.image import Image
import pkg_resources

if 'COVERAGE_PROCESS_START' in os.environ:
    EXECUTABLE = ["coverage", "run"]
else:
    EXECUTABLE = [sys.executable]

TEST_DATA_DIR = pkg_resources.resource_filename(__name__, "test_commandline-data")

FIXTURES = [
    {
        "remove": ("dummy.pdf",),
        "command": ["-n", "0", "-p", "a4"],
        "returncode": 0,
        "diff": ("dummy.pdf", os.path.join(TEST_DATA_DIR, "zero.pdf"))
    },
    {
        "remove": ("dummy.pdf",),
        "command": ["--papersize", "0cmx1cm"],
        "returncode": 0,
        "diff": ("dummy.pdf", os.path.join(TEST_DATA_DIR, "null.pdf"))
    },
    {
        "remove": ("dummy.pdf",),
        "command": ["-n", "10", "--start", "20", "--papersize", "10cmx100mm"],
        "returncode": 0,
        "diff": ("dummy.pdf", os.path.join(TEST_DATA_DIR, "twenty.pdf"))
    },
    {
        "remove": ("dummy.pdf",),
        "command": [],
        "returncode": 0,
        "diff": ("dummy.pdf", os.path.join(TEST_DATA_DIR, "default.pdf"))
    },
    {
        "remove": ("dummy.pdf",),
        "command": ["--list", "a4", "a5:2", "a6:0", "10cmx100mm", "10cmx100mm"],
        "returncode": 0,
        "diff": ("dummy.pdf", os.path.join(TEST_DATA_DIR, "list.pdf"))
    },
    # Errors
    {
        "command": ["-n", "1", "-l", "a4"],
        "returncode": 1,
        "stderr": "Options '--number' and '--papersize' are incompatible with option '--list'.\n",
    },
    {
        "command": ["-p", "a4", "-l", "a4"],
        "returncode": 1,
        "stderr": "Options '--number' and '--papersize' are incompatible with option '--list'.\n",

    },
    {
        "command": ["-p", "0cmx0cm"],
        "returncode": 1,
        "stderr": "Error: I cannot produce pages with dimension 0x0.\n",
    },
]

class TestCommandLine(unittest.TestCase):
    """Run binary, and check produced files."""

    def assertPdfEqual(self, filea, fileb):
        """Test whether PDF files given in argument (as file names) are equal.

        Equal means: they look the same.
        """
        # pylint: disable=invalid-name
        images = (
            Image(filename=filea),
            Image(filename=fileb),
            )

        # Check that files have the same number of pages
        self.assertEqual(
            len(images[0].sequence),
            len(images[1].sequence),
            )

        # Check if pages look the same
        for (pagea, pageb) in zip(images[0].sequence, images[1].sequence):
            self.assertEqual(
                pagea.compare(pageb, metric="absolute")[1],
                0,
                )

    # If tests are really needed for python3.4, a kind-of backport of
    # subprocess.run() is available here:
    # https://framagit.org/spalax/pdfimpose/blob/bc5f72f91cbae589f126e0509f52a2a6c3eee43c/test/test_commandline.py#L49-68
    @unittest.skipIf(sys.version_info < (3, 5), "Tests require python version 3.5 or higher.")
    def test_commandline(self):
        """Test binary, from command line to produced files."""
        for data in FIXTURES:
            with self.subTest(**data):
                for filename in data.get('remove', ()):
                    try:
                        os.remove(filename)
                    except FileNotFoundError:
                        pass
                completed = subprocess.run(
                    EXECUTABLE + ["-m", "dummypdf"] + data['command'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    )

                for key in ["returncode", "stderr", "stdout"]:
                    if key in data:
                        self.assertEqual(
                            getattr(completed, key),
                            data.get(key),
                            )

                if "diff" in data:
                    self.assertPdfEqual(*data['diff'])
