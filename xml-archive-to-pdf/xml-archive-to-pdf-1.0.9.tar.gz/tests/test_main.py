import unittest
import os.path
from xml_archive_to_pdf.main import main


"""
Main unit tests
"""


class MainTest(unittest.TestCase):

    def setUp(self):
        self.xml_file = "tests/data/pathfinder_1.xml"
        self.pdf_file = "tests/data/pathfinder_1.pdf"
        self.logo_file = "tests/data/logo.png"
        self.font_folder = "tests/data/CustomFont"
        self.args = {
            "--input": self.xml_file,
            "--output": self.pdf_file,
            "--logo": self.logo_file,
            "--font": self.font_folder
        }

    def test_main(self):
        if os.path.exists(self.pdf_file):
            os.remove(self.pdf_file)
        main(args=self.args)
        self.assertTrue(os.path.exists(self.pdf_file))
        self.assertTrue(os.path.getsize(self.pdf_file) > 0)
