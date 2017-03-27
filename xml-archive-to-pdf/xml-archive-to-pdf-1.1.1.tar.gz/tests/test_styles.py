import unittest
from xml_archive_to_pdf.styles import get_styles, get_title_style, get_normal_style, get_table_style
from xml_archive_to_pdf.utils import registerFont
import xml.etree.cElementTree as ET
from reportlab.platypus import TableStyle

"""
Styles unit tests
"""


class StylesTest(unittest.TestCase):

    def setUp(self):
        self.xml_file = "tests/data/pathfinder_1.xml"
        self.tree = ET.parse(self.xml_file)
        self.pdf_file = "tests/data/pathfinder_1_tmp.pdf"
        self.font_folder = "tests/data/CustomFont"
        self.logo_file = "tests/data/logo.png"
        self.styles = get_styles()

    def test_get_styles_without_font(self):
            styles = self.styles
            self.assertIsNotNone(styles["cTitle"])
            self.assertEqual(styles["cTitle"].fontName, "Helvetica-Bold")
            self.assertEqual(0, styles["cTitle"].leftIndent)
            self.assertIsNotNone(styles["cHeading1"])
            self.assertEqual(styles["cHeading1"].fontName, "Helvetica-Bold")
            self.assertEqual(0, styles["cHeading1"].leftIndent)
            self.assertIsNotNone(styles["cHeading2"])
            self.assertEqual(styles["cHeading2"].fontName, "Helvetica-Bold")
            self.assertEqual(12, styles["cHeading2"].leftIndent)
            self.assertIsNotNone(styles["cHeading3"])
            self.assertEqual(styles["cHeading3"].fontName, "Helvetica-BoldOblique")
            self.assertEqual(24, styles["cHeading3"].leftIndent)
            self.assertIsNotNone(styles["cHeading4"])
            self.assertEqual(styles["cHeading4"].fontName, "Helvetica-BoldOblique")
            self.assertEqual(36, styles["cHeading4"].leftIndent)
            self.assertIsNotNone(styles["cHeading5"])
            self.assertEqual(styles["cHeading5"].fontName, "Helvetica-Bold")
            self.assertEqual(48, styles["cHeading5"].leftIndent)
            self.assertIsNotNone(styles["cHeading6"])
            self.assertEqual(styles["cHeading6"].fontName, "Helvetica-Bold")
            self.assertEqual(60, styles["cHeading6"].leftIndent)
            self.assertIsNotNone(styles["cNormal"])
            self.assertEqual(styles["cNormal"].fontName, "Helvetica")
            self.assertEqual(0, styles["cNormal"].leftIndent)
            self.assertIsNotNone(styles["cNormal1"])
            self.assertEqual(styles["cNormal1"].fontName, "Helvetica")
            self.assertEqual(12, styles["cNormal1"].leftIndent)
            self.assertIsNotNone(styles["cNormal2"])
            self.assertEqual(styles["cNormal2"].fontName, "Helvetica")
            self.assertEqual(24, styles["cNormal2"].leftIndent)
            self.assertIsNotNone(styles["cNormal3"])
            self.assertEqual(styles["cNormal3"].fontName, "Helvetica")
            self.assertEqual(36, styles["cNormal3"].leftIndent)
            self.assertIsNotNone(styles["cNormal4"])
            self.assertEqual(styles["cNormal4"].fontName, "Helvetica")
            self.assertEqual(48, styles["cNormal4"].leftIndent)
            self.assertIsNotNone(styles["cNormal5"])
            self.assertEqual(styles["cNormal5"].fontName, "Helvetica")
            self.assertEqual(60, styles["cNormal5"].leftIndent)
            self.assertIsNotNone(styles["cNormal6"])
            self.assertEqual(styles["cNormal6"].fontName, "Helvetica")
            self.assertEqual(72, styles["cNormal6"].leftIndent)
            self.assertIsNotNone(styles["cBodyText"])
            self.assertEqual(styles["cBodyText"].fontName, "Helvetica")
            self.assertEqual(0, styles["cBodyText"].leftIndent)
            self.assertIsNotNone(styles["cItalic"])
            self.assertEqual(styles["cItalic"].fontName, "Helvetica-Oblique")
            self.assertEqual(0, styles["cItalic"].leftIndent)

    def test_get_styles_with_font(self):
        if self.font_folder:
            registerFont("CustomFont", self.font_folder)
            styles = get_styles("CustomFont")
            self.assertIsNotNone(styles["cTitle"])
            self.assertEqual(styles["cTitle"].fontName, "CustomFont-Bold")
            self.assertEqual(0, styles["cTitle"].leftIndent)
            self.assertIsNotNone(styles["cHeading1"])
            self.assertEqual(styles["cHeading1"].fontName, "CustomFont-Bold")
            self.assertEqual(0, styles["cHeading1"].leftIndent)
            self.assertIsNotNone(styles["cHeading2"])
            self.assertEqual(styles["cHeading2"].fontName, "CustomFont-Bold")
            self.assertEqual(12, styles["cHeading2"].leftIndent)
            self.assertIsNotNone(styles["cHeading3"])
            self.assertEqual(styles["cHeading3"].fontName, "CustomFont-BoldOblique")
            self.assertEqual(24, styles["cHeading3"].leftIndent)
            self.assertIsNotNone(styles["cHeading4"])
            self.assertEqual(styles["cHeading4"].fontName, "CustomFont-BoldOblique")
            self.assertEqual(36, styles["cHeading4"].leftIndent)
            self.assertIsNotNone(styles["cHeading5"])
            self.assertEqual(styles["cHeading5"].fontName, "CustomFont-Bold")
            self.assertEqual(48, styles["cHeading5"].leftIndent)
            self.assertIsNotNone(styles["cHeading6"])
            self.assertEqual(styles["cHeading6"].fontName, "CustomFont-Bold")
            self.assertEqual(60, styles["cHeading6"].leftIndent)
            self.assertIsNotNone(styles["cNormal"])
            self.assertEqual(styles["cNormal"].fontName, "CustomFont")
            self.assertEqual(0, styles["cNormal"].leftIndent)
            self.assertIsNotNone(styles["cNormal1"])
            self.assertEqual(styles["cNormal1"].fontName, "CustomFont")
            self.assertEqual(12, styles["cNormal1"].leftIndent)
            self.assertIsNotNone(styles["cNormal2"])
            self.assertEqual(styles["cNormal2"].fontName, "CustomFont")
            self.assertEqual(24, styles["cNormal2"].leftIndent)
            self.assertIsNotNone(styles["cNormal3"])
            self.assertEqual(styles["cNormal3"].fontName, "CustomFont")
            self.assertEqual(36, styles["cNormal3"].leftIndent)
            self.assertIsNotNone(styles["cNormal4"])
            self.assertEqual(styles["cNormal4"].fontName, "CustomFont")
            self.assertEqual(48, styles["cNormal4"].leftIndent)
            self.assertIsNotNone(styles["cNormal5"])
            self.assertEqual(styles["cNormal5"].fontName, "CustomFont")
            self.assertEqual(60, styles["cNormal5"].leftIndent)
            self.assertIsNotNone(styles["cNormal6"])
            self.assertEqual(styles["cNormal6"].fontName, "CustomFont")
            self.assertEqual(72, styles["cNormal6"].leftIndent)
            self.assertIsNotNone(styles["cBodyText"])
            self.assertEqual(styles["cBodyText"].fontName, "CustomFont")
            self.assertEqual(0, styles["cBodyText"].leftIndent)
            self.assertIsNotNone(styles["cItalic"])
            self.assertEqual(styles["cItalic"].fontName, "CustomFont-Oblique")
            self.assertEqual(0, styles["cItalic"].leftIndent)

    def test_get_title_style(self):
        self.assertEqual(get_title_style(self.styles, 3).name, "cHeading3")
        self.assertEqual(get_title_style(self.styles, 50).name, "cItalic")
        self.assertEqual(get_title_style(self.styles, -1).name, "cItalic")

    def test_get_normal_style(self):
        self.assertEqual(get_normal_style(self.styles, 3).name, "cNormal3")
        self.assertEqual(get_normal_style(self.styles, 50).name, "cNormal6")
        self.assertEqual(get_normal_style(self.styles, -1).name, "cNormal6")

    def test_get_table_style(self):
        ts = get_table_style()
        self.assertTrue(isinstance(ts, TableStyle))
