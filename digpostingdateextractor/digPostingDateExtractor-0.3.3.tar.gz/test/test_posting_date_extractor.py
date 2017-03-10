import unittest

from digExtractor.extractor_processor import ExtractorProcessor
from digPostingDateExtractor.posting_date_extractor import PostingDateExtractor


class TestDrugUseExtractorMethods(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_posting_extractor(self):
        doc = {'content': 'online: Jul 07, 00:44 \n  ', 'b': 'world'}

        extractor = PostingDateExtractor().set_metadata(
            {'extractor': 'posting_date'})
        extractor_processor = ExtractorProcessor().set_input_fields(
            ['content']).set_output_field('extracted').set_extractor(extractor)
        updated_doc = extractor_processor.extract(doc)
        self.assertEqual(updated_doc['extracted'][0]['result']['value'],
                         '2016-07-07')


if __name__ == '__main__':
    unittest.main()
