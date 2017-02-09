
import unittest

import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import groundtruth

from digExtractor.extractor_processor import ExtractorProcessor
from digPhoneExtractor.phone_extractor import PhoneExtractor

class TestPhoneExtractorMethods(unittest.TestCase):

    def setUp(self):
        self.groundtruth_data = groundtruth.load_groundtruth()

    def tearDown(self):
        pass

    def test_phone_extractor(self):
        #'Sexy new girl in town searching for a great date wiff u Naughty fresh girl here searching 4 a great date wiff you Sweet new girl in town seeking for a good date with u for80 2sixseven one9zerofor 90hr incall or out call'
        doc = {'content': [u'Sexy', u'new', u'girl', u'in', 'town', 'searching', 'for', 'a', 'great', 'date', 'wiff', 'u', 'Naughty', 'fresh', 'girl', 'here', 'searching', '4', 'a', 'great', 'date', 'wiff', 'you', 'Sweet', 'new', 'girl', 'in', 'town', 'seeking', 'for', 'a', 'good', 'date', 'with', 'u', 'for80', '2sixseven', 'one9zerofor', '90hr', 'incall', 'or', 'out', 'call'],
               'url': u'http://liveescortreviews.com/ad/philadelphia/602-228-4192/1/310054', 'b': 'world'}

        e1 = PhoneExtractor().set_metadata({'extractor': 'phone'})
        e1.set_source_type('url')
        ep1 = ExtractorProcessor().set_input_fields('url')\
                                  .set_output_field('extracted')\
                                  .set_extractor(e1)
        updated_doc = ep1.extract(doc)
        e2 = PhoneExtractor().set_metadata({'extractor': 'phone'})
        e2.set_source_type('text')
        ep2 = ExtractorProcessor().set_input_fields('content')\
                                  .set_output_field('extracted')\
                                  .set_extractor(e2)
        updated_doc = ep2.extract(updated_doc)

        result1 = updated_doc['extracted'][0]['result']
        result2 = updated_doc['extracted'][1]['result']
        self.assertEqual(result1[0]['value'], '6022284192')
        self.assertEqual(result2[0]['value'], '4802671904')

    def test_phone_extractor_with_context(self):
        doc = {'content': ['Sexy', 'new', 'girl', 'in', 'town', 'searching', 'for', 'a', 'great', 'date', 'wiff', 'u', 'Naughty', 'fresh', 'girl', 'here', 'searching', '4', 'a', 'great', 'date', 'wiff', 'you', 'Sweet', 'new', 'girl', 'in', 'town', 'seeking', 'for', 'a', 'good', 'date', 'with', 'u', 'for80', '2sixseven', 'one9zerofor', '90hr', 'incall', 'or', 'out', 'call'],
               'url': 'http://liveescortreviews.com/ad/philadelphia/602-228-4192/1/310054', 'b': 'world'}

        e1 = PhoneExtractor().set_metadata({'extractor': 'phone'})
        e1.set_source_type('url')
        e1.set_include_context(True)
        ep1 = ExtractorProcessor().set_input_fields('url')\
                                  .set_output_field('extracted')\
                                  .set_extractor(e1)
        updated_doc = ep1.extract(doc)
        e2 = PhoneExtractor().set_metadata({'extractor': 'phone'})
        e2.set_source_type('text')
        e2.set_include_context(True)
        ep2 = ExtractorProcessor().set_input_fields('content')\
                                  .set_output_field('extracted')\
                                  .set_extractor(e2)
        updated_doc = ep2.extract(updated_doc)

        result1 = updated_doc['extracted'][0]['result']
        result2 = updated_doc['extracted'][1]['result']
        self.assertEqual(result1[0]['value'], '6022284192')
        self.assertEqual(result2[0]['value'], '4802671904')


if __name__ == '__main__':
    unittest.main()
