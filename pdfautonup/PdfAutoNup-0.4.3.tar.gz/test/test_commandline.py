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
        "command": [
            "--algorithm", "panel", "--gap", ".5cm", "--margin", "1cm",
            os.path.join(TEST_DATA_DIR, "pcb.pdf"),
            ],
        "returncode": 0,
        "diff": ("pcb-nup.pdf", "pcb-control.pdf")
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "trigo.pdf")],
        "returncode": 0,
        "diff": ("trigo-nup.pdf", "trigo-control.pdf")
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "three-pages.pdf")],
        "returncode": 0,
        "diff": ("three-pages-nup.pdf", "three-pages-control.pdf")
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "malformed.pdf")],
        "returncode": 1,
        "stderr": "Error while reading file '{}': Could not read malformed PDF file.\n".format(
            os.path.join(TEST_DATA_DIR, "malformed.pdf")
            ),
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "zero-pages.pdf")],
        "returncode": 1,
        "stderr": "Error: PDF files have no pages to process.\n",
    },
    {
        "command": [os.path.join(TEST_DATA_DIR, "dummy.pdf")],
        "returncode": 1,
        "stderr": "Error: A PDF page have a null dimension.\n",
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
                completed = subprocess.run(
                    EXECUTABLE + ["-m", "pdfautonup"] + data['command'],
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
                    self.assertPdfEqual(*(
                        os.path.join(TEST_DATA_DIR, filename)
                        for filename in data['diff']
                        ))
