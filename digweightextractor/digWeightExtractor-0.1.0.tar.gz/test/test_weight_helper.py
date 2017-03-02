import re
import unittest

from digWeightExtractor.weight_helper import *


class TestReviewIDExtractorMethods(unittest.TestCase):

    def setUp(self):
        self.hw = WeightHelper()

    def tearDown(self):
        pass

    def test_us_weight(self):

        ################################################
        #   Test Unit Solution Regs for Weight
        ################################################

        # test reg_us_weight_unit_lb
        regex = re.compile(reg_us_weight_unit_lb)
        self.assertEqual(regex.findall('105lbs'), ["105lbs"])
        self.assertEqual(regex.findall('105 lbs'), ["105 lbs"])

        # test reg_us_weight_unit_kg
        regex = re.compile(reg_us_weight_unit_kg)
        self.assertEqual(regex.findall('53kg'), ["53kg"])
        self.assertEqual(regex.findall('53 kg'), ["53 kg"])

        ################################################
        #   Main Test Unit Solution Regs for Height
        ################################################

        # test re_us_weight
        regex = re.compile(re_us_weight)
        self.assertEqual(regex.findall('105lbs'), ["105lbs"])
        self.assertEqual(regex.findall('53kg'), ["53kg"])

    def test_ls_weight(self):
        ################################################
        #   Test Label Solution Regs for Weight
        ################################################

        # test reg_ls_weight
        regex = re.compile(reg_ls_weight, re.IGNORECASE)
        self.assertEqual(regex.findall('Weight: \n 53'), [": \n 53"])
        self.assertEqual(regex.findall('Weight   : \n 53'), ["   : \n 53"])

        ################################################
        #   Main Label Unit Solution Regs for Weigth
        ################################################
        regex = re.compile(reg_ls_weight, re.IGNORECASE)
        self.assertEqual(regex.findall('Weight: \n 53'), [": \n 53"])

    def test_extract_weight(self):
        text = "\n TS RUBI: THE NAME SAYS IT ALL!  \n INCALL $250 OUTCALL $350 \n \n \n \n \n \n Gender \n " \
               "Age \n Ethnicity \n Hair Color \n Eye Color \n Height \n Weight \n Measurements \n Affiliation \n " \
               "Availability \n Available To \n \n \n \n \n Transsexual \n 27 \n Latino/Hispanic \n Brown \n Hazel " \
               "\n 5'5\" \n 130 lb \n 34C - 28\" - 34\" \n "
        self.assertEqual(self.hw.extract(text), {'weight': {'raw': [{'pound': 130}], 'pound': [130], 'kilogram': [
                         58]}})

        text = "\n \n Height: \r\n                          5'3''\r\n                    " \
               "   \n \n \n \n \n \n Weight: \r\n                          125 lbs\r\n         " \
               "              \n \n \n \n \n \n"
        self.assertEqual(self.hw.extract(text), {'weight': {'raw': [{'pound': 125}], 'pound': [125], 'kilogram': [
                         56]}})

        text = "Breasts DD Eyes gray Height 1.52 Skin Tanned Weight 60"
        self.assertEqual(self.hw.extract(text), {'weight': {'raw': [{'kilogram': 60}], 'pound': [132], 'kilogram': [
                         60]}})


if __name__ == '__main__':
    unittest.main()
