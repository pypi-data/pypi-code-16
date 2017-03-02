# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-11-08 14:50:34
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-11-13 15:32:04
import unittest

import groundtruth
from digExtractor.extractor_processor import ExtractorProcessor
from digHeightExtractor.height_extractor import HeightExtractor


class TestGroundtruthMethods(unittest.TestCase):

    def setUp(self):
        self.groundtruth_data = groundtruth.load_groundtruth()

    def tearDown(self):
        pass

    def test_height_extractor(self):
        extractor = HeightExtractor().set_metadata(
            {'extractor': 'height_weight'})
        extractor_processor = ExtractorProcessor().set_input_fields(
            ['content']).set_output_field('extracted').set_extractor(extractor)

        for doc in self.groundtruth_data[:20]:
            updated_doc = extractor_processor.extract(doc)
            self.assertIn('extracted', updated_doc)
            self.assertTrue(len(updated_doc['extracted']) > 0)
            extraction = updated_doc['extracted'][0]['result']['value']

            if 'height' in doc:
                self.assertIn('height', extraction)
                self.assertEqual(extraction['height'], doc['height'])

if __name__ == '__main__':
    unittest.main()
