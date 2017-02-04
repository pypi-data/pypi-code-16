import unittest


class svgTest(unittest.TestCase):

    def assert_numeric_attributes(self, svg_element, attributes):
        for att in attributes:
            self.assertIsInstance(svg_element.attribs[att], (int, float))
