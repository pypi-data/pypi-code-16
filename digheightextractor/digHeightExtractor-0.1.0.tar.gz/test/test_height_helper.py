import re
import unittest

from digHeightExtractor.height_helper import *


class TestReviewIDExtractorMethods(unittest.TestCase):

    def setUp(self):
        self.hw = HeightHelper()

    def tearDown(self):
        pass

    def test_us_height(self):

        ################################################
        #   Test Unit Solution Regs for Height
        ################################################

        # test reg_us_height_symbol
        regex = re.compile(reg_us_height_symbol)
        self.assertEqual(regex.findall('Height: 5\'4\"'), ["5'4"])
        self.assertEqual(regex.findall('Height: 5\'\'4\"'), ["5''4"])
        self.assertEqual(regex.findall('Height: 5\' 4'), ["5' 4"])

        # test reg_us_height_unit_cm
        regex = re.compile(reg_us_height_unit_cm)
        self.assertEqual(regex.findall('129cm'), ["129cm"])

        # test reg_us_height_unit_ft
        regex = re.compile(reg_us_height_unit_ft)
        self.assertEqual(regex.findall('5ft'), ["5ft"])
        self.assertEqual(regex.findall('5.5ft'), ["5.5ft"])
        self.assertEqual(regex.findall('5.5ft5in'), ["5.5ft5in"])
        self.assertEqual(regex.findall('5.5ft 4in'), ["5.5ft 4in"])

        ################################################
        #   Main Test Unit Solution Regs for Height
        ################################################

        # test re_us_height
        regex = re.compile(re_us_height)
        self.assertEqual(regex.findall('Height: 5\'4\"'), ["5'4"])
        self.assertEqual(regex.findall('129cm'), ["129cm"])
        self.assertEqual(regex.findall('5.5ft5in'), ["5.5ft5in"])

    def test_ls_height(self):
        ################################################
        #   Test Label Solution Regs for Height
        ################################################

        # test reg_ls_height
        regex = re.compile(reg_ls_height, re.IGNORECASE)
        self.assertEqual(regex.findall('Height: \n 170'), [": \n 170"])
        self.assertEqual(regex.findall('Height: \n 5.7'), [": \n 5.7"])
        self.assertEqual(regex.findall('Height: 1.52'), [": 1.52"])
        self.assertEqual(regex.findall('Height: 272cm'), [": 272cm"])
        self.assertEqual(regex.findall('Height:\n 5ft'), [":\n 5ft"])
        self.assertEqual(regex.findall('Height:\n 5ft3in'), [":\n 5ft3in"])

        ################################################
        #   Main Label Unit Solution Regs for Height
        ################################################
        regex = re.compile(reg_ls_height, re.IGNORECASE)
        self.assertEqual(regex.findall('Height: \n 170'), [": \n 170"])
        self.assertEqual(regex.findall('Height: 272cm'), [": 272cm"])


    def test_extract_height(self):
        text = "\n TS RUBI: THE NAME SAYS IT ALL!  \n INCALL $250 OUTCALL $350 \n \n \n \n \n \n Gender \n Age " \
               "\n Ethnicity \n Hair Color \n Eye Color \n Height \n Weight \n Measurements \n Affiliation \n " \
               "Availability \n Available To \n \n \n \n \n Transsexual \n 27 \n Latino/Hispanic \n Brown \n Hazel " \
               "\n 5'5\" \n 130 lb \n 34C - 28\" - 34\" \n "
        self.assertEqual(self.hw.extract(text), {'height': {'foot': ['5\'5"'],
                                                            'raw': [{'foot': 5, 'inch': 5}], 'centimeter': [165]}})

        text = "\n \n Height: \r\n                          5'3''\r\n              " \
               "         \n \n \n \n \n \n Weight: \r\n                          125 lbs\r\n                " \
               "       \n \n \n \n \n \n"
        self.assertEqual(self.hw.extract(text), {'height': {'foot': ['5\'3"'],
                                                            'raw': [{'foot': 5, 'inch': 3}], 'centimeter': [160]}})

        text = "Breasts DD Eyes gray Height 1.52 Skin Tanned Weight 60"
        self.assertEqual(self.hw.extract(text), {'height': {'foot': ['4\'11"'], 'raw': [{'centimeter': 52, 'meter': 1}],
                                                            'centimeter': [152]}})


if __name__ == '__main__':
    unittest.main()
