import unittest
import os
from xml_archive_to_pdf.utils import get_bare_tag, get_clean_text, get_doc, \
registerFont, get_label, has_children, add_logo, ptTomm, write_table, write_elem, \
is_writable_element, calcul_level, is_leaving_table, build_pdf, is_started_table
import xml.etree.cElementTree as ET
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus.flowables import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, Indenter
from xml_archive_to_pdf.styles import get_styles

"""
Utils unit tests
"""


class UtilsTest(unittest.TestCase):

    def setUp(self):
        self.xml_file = "tests/data/pathfinder_1.xml"
        self.tree = ET.parse(self.xml_file)
        self.pdf_file = "tests/data/pathfinder_1_tmp.pdf"
        self.font_folder = "tests/data/CustomFont"
        self.logo_file = "tests/data/logo.png"

    def test_build_pdf(self):
        build_pdf(self.xml_file, self.pdf_file, self.logo_file, self.font_folder)
        self.assertTrue(os.path.exists(self.pdf_file))
        self.assertTrue(os.path.getsize(self.pdf_file) > 0)

    def test_get_bare_tag(self):
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}element")
        bare_tag = get_bare_tag(elem)
        self.assertEqual(bare_tag, "element")

    def test_get_clean_text(self):
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}qualite")
        clean_text = get_clean_text(elem)
        self.assertEqual(clean_text, "très bonne")

    def test_get_doc(self):
        doc = get_doc(self.pdf_file)
        self.assertEqual(doc.pagesize, (612.0, 792.0))
        self.assertEqual(doc.bottomMargin, 12*2)
        self.assertEqual(doc.topMargin, 12*2)
        self.assertEqual(doc.leftMargin, 12*2)
        self.assertEqual(doc.rightMargin, 12*2)

    def test_registerFont(self):
        registerFont("CustomFont", self.font_folder)
        self.assertIsNotNone(pdfmetrics.getFont("CustomFont"))

    def test_get_label(self):
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}element")
        self.assertEqual(get_label(elem), "élément")
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}niveau")
        self.assertEqual(get_label(elem), "niveau")
        elem = self.tree.findall(".//{fr:unistra:di:archive:pathfinder:v1}classe")[1]
        self.assertEqual(get_label(elem), "")

    def test_has_children(self):
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}element")
        self.assertFalse(has_children(elem))
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}classes")
        self.assertTrue(has_children(elem))

    def test_add_logo(self):
        Story = []
        add_logo(Story, self.logo_file)
        self.assertTrue(isinstance(Story[0], Image))
        self.assertTrue(isinstance(Story[1], Spacer))

    def test_ptTomm(self):
        r = ptTomm(3)
        self.assertEqual(r, 1.0583339999999999)

    def test_write_table(self):
        Story = []
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}armes")
        write_table(Story, elem, 2, get_styles())
        self.assertEqual(len(Story), 3)
        # 0
        self.assertEqual(Story[0].style.name, "cHeading2")
        self.assertEqual(Story[0].text, "Liste des armes")
        # 1
        self.assertTrue(isinstance(Story[1], Spacer))
        # 2
        self.assertTrue(isinstance(Story[2], Table))
        # table
        self.assertEqual(Story[2]._colWidths,
            [67.99611118110236, 67.99611118110236, 67.99611118110236, 67.99611118110236,
             67.99611118110236, 67.99611118110236, 67.99611118110236, 67.99611118110236])
        self.assertEqual(len(Story[2].__dict__["_cellvalues"]), 4)
        self.assertEqual(len(Story[2].__dict__["_cellvalues"][0]), 8)
        self.assertEqual(len(Story[2].__dict__["_cellvalues"][1]), 8)
        self.assertEqual(len(Story[2].__dict__["_cellvalues"][2]), 8)
        self.assertEqual(len(Story[2].__dict__["_cellvalues"][3]), 8)
        # Column titles
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][0].text, "<b>nom</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][1].text, "<b>type</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][2].text, "<b>portée</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][3].text, "<b>dégât</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][4].text, "<b>élément</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][5].text, "<b>rareté</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][6].text, "<b>prix</b>")
        self.assertEqual(Story[2].__dict__["_cellvalues"][0][7].text, "<b>qualité</b>")
        # First row
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][0].text, "cimeterre")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][1].text, "à deux mains")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][2].text, "3")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][3].text, "7")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][4].text, "feu")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][5].text, "épique")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][6].text, "1000")
        self.assertEqual(Story[2].__dict__["_cellvalues"][1][7].text, "très bonne")
        # Second row
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][0].text, "arc")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][1].text, "à distance")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][2].text, "8")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][3].text, "2")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][4].text, "glace")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][5].text, "simple")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][6].text, "100")
        self.assertEqual(Story[2].__dict__["_cellvalues"][2][7].text, "mauvaise")
        # Thrid row
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][0].text, "épée")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][1].text, "à une main")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][2].text, "5")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][3].text, "3")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][4].text, "terre")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][5].text, "rare")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][6].text, "500")
        self.assertEqual(Story[2].__dict__["_cellvalues"][3][7].text, "moyenne")

    def test_write_elem(self):
        Story = []
        # title
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}etat-civil")
        write_elem(Story, elem, 1, get_styles())
        self.assertEqual(len(Story), 1)
        self.assertEqual(Story[0].text, "son état civil")
        self.assertEqual(Story[0].style.name, "cHeading1")
        # key value
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}age")
        write_elem(Story, elem, 2, get_styles(), 2)
        self.assertEqual(len(Story), 2)
        self.assertEqual(Story[1].text, "<b>son âge :</b> 20")
        self.assertEqual(Story[1].style.name, "cNormal2")
        # forced title
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}quetes")
        write_elem(Story, elem, 1, get_styles())
        self.assertEqual(len(Story), 3)
        self.assertEqual(Story[2].text, "Quêtes en cours")
        self.assertEqual(Story[2].style.name, "cHeading1")

    def test_is_writable_element(self):
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}etat-civil")
        r = is_writable_element(elem, "start", (False, 0))
        self.assertTrue(r)
        r = is_writable_element(elem, "start", (True, 1))
        self.assertFalse(r)
        r = is_writable_element(elem, "end", (False, 0))
        self.assertFalse(r)

    def test_is_started_tablet(self):
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}armes")
        r = is_started_table(elem, "start", (False, 0))
        self.assertTrue(r)
        r = is_started_table(elem, "start", (True, 1))
        self.assertFalse(r)
        r = is_started_table(elem, "end", (False, 0))
        self.assertFalse(r)
        elem = self.tree.find(".//{fr:unistra:di:archive:pathfinder:v1}etat-civil")
        r = is_started_table(elem, "start", (False, 0))
        self.assertFalse(r)
        r = is_started_table(elem, "start", (True, 1))
        self.assertFalse(r)
        r = is_started_table(elem, "end", (False, 0))
        self.assertFalse(r)

    def test_calcul_level(self):
        self.assertEqual(4, calcul_level("start", 3))
        self.assertEqual(5, calcul_level("end", 6))

    def test_is_leaving_table(self):
        self.assertFalse(is_leaving_table("start", 3, (False, 0)))
        self.assertFalse(is_leaving_table("start", 3, (True, 2)))
        self.assertFalse(is_leaving_table("start", 3, (True, 3)))
        self.assertFalse(is_leaving_table("end", 3, (False, 0)))
        self.assertFalse(is_leaving_table("end", 3, (True, 2)))
        self.assertTrue(is_leaving_table("end", 3, (True, 3)))

    def tearDown(self):
        if os.path.exists(self.pdf_file):
            os.remove(self.pdf_file)
