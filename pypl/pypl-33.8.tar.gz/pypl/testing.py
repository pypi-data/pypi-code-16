import unittest


class svgTest(unittest.TestCase):

    def assert_numeric_attributes(self, svg_element, attributes):
        for att in attributes:
            if isinstance(svg_element.attribs[att], str):
                try:
                    val = svg_element.attribs[att]
                    svg_element.attribs[att] = float(val)
                except ValueError:
                    # in this case it will fail more meaningfully on next line
                    pass
            self.assertIsInstance(svg_element.attribs[att], (int, float))
