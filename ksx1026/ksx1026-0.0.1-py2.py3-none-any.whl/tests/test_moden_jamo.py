"""
Tests for modern jamo
"""

from ksx1026 import uchar, normalization
import unittest

class JamoTest(unittest.TestCase):

    def setUp(self):
        self.lchar = list( chr(x) for x in range(int("1100", 16), int("1112", 16) + 1))
        self.vchar = list( chr(x) for x in range(int("1161", 16), int("1175", 16) + 1))
        self.tchar = list( chr(x) for x in range(int("11A8", 16), int("11C2", 16) + 1))

    def test_uchar(self):
        for l in self.lchar:
            self.assertTrue(uchar.isModernChoseong(l))
            self.assertTrue(uchar.isChoseongJamo(l))
            self.assertFalse(uchar.isModernJungseong(l))
            self.assertFalse(uchar.isJungseongJamo(l))
            self.assertFalse(uchar.isModernJongseong(l))
            self.assertFalse(uchar.isOldJongseong(l))
            self.assertFalse(uchar.isJongseongJamo(l))
            self.assertTrue(uchar.isHangulJamo(l))
            self.assertFalse(uchar.isHalfwidthLetter(l))
            self.assertFalse(uchar.isCompatibilityLetter(l))
            self.assertFalse(uchar.isParenthesizedLetter(l))
            self.assertFalse(uchar.isCircledLetter(l))
            self.assertFalse(uchar.isPrecomposedSyllable(l))
            self.assertTrue(uchar.isHangulLetter(l))

        for v in self.vchar:
            self.assertFalse(uchar.isModernChoseong(v))
            self.assertFalse(uchar.isChoseongJamo(v))
            self.assertTrue(uchar.isModernJungseong(v))
            self.assertTrue(uchar.isJungseongJamo(v))
            self.assertFalse(uchar.isModernJongseong(v))
            self.assertFalse(uchar.isOldJongseong(v))
            self.assertFalse(uchar.isJongseongJamo(v))
            self.assertTrue(uchar.isHangulJamo(v))
            self.assertFalse(uchar.isHalfwidthLetter(v))
            self.assertFalse(uchar.isCompatibilityLetter(v))
            self.assertFalse(uchar.isParenthesizedLetter(v))
            self.assertFalse(uchar.isCircledLetter(v))
            self.assertFalse(uchar.isPrecomposedSyllable(v))
            self.assertTrue(uchar.isHangulLetter(v))

        for t in self.tchar:
            self.assertFalse(uchar.isModernChoseong(t))
            self.assertFalse(uchar.isChoseongJamo(t))
            self.assertFalse(uchar.isModernJungseong(t))
            self.assertFalse(uchar.isJungseongJamo(t))
            self.assertTrue(uchar.isModernJongseong(t))
            self.assertFalse(uchar.isOldJongseong(t))
            self.assertTrue(uchar.isJongseongJamo(t))
            self.assertTrue(uchar.isHangulJamo(t))
            self.assertFalse(uchar.isHalfwidthLetter(t))
            self.assertFalse(uchar.isCompatibilityLetter(t))
            self.assertFalse(uchar.isParenthesizedLetter(t))
            self.assertFalse(uchar.isCircledLetter(t))
            self.assertFalse(uchar.isPrecomposedSyllable(t))
            self.assertTrue(uchar.isHangulLetter(t))

    def test_normalization(self):
        for l in self.lchar:
            self.assertEqual(normalization.composeHangul(l),l + chr(int("1160",16)) )


