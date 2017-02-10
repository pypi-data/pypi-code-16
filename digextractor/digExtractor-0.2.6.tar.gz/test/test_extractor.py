import unittest

from digExtractor.extractor import Extractor
from digExtractor.extractor_processor import ExtractorProcessor
from digExtractor.extractor_processor_chain import execute_processor_chain

class SampleSingleRenamedFieldExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = 'c'

    def extract(self, doc):
        return doc['c']

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields;

class SampleMultipleRenamedFieldExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = ['c','d']

    def extract(self, doc):
        return doc['c'] + doc['d']

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields;

class SampleSingleRenamedFieldMultipleOutputsExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = 'c'

    def extract(self, doc):
        extracted = dict()
        extracted['f'] = doc[self.renamed_input_fields]
        extracted['g'] = doc[self.renamed_input_fields]
        return extracted

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields;

class TestExtractor(unittest.TestCase):

    def test_single_renamed_field_extractor(self):
        doc = { 'a': 'hello', 'b': 'world'}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields('a').set_output_field('e').set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_missing_extractor(self):
        doc = { 'b': 'world'}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields('a').set_output_field('e').set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertTrue('e' not in updated_doc)
        self.assertEqual(updated_doc['b'], 'world')

    def test_nested_field_filtered_extractor(self):
        doc = { 'a':[{'b': 'world', 'c': 'good'}, {'b': 'cup', 'c': 'bad'}]}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields('a[?c=good].b').set_output_field('e').set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['value'], 'world')

    def test_multiple_renamed_field_extractor(self):
        doc = { 'a': 'hello', 'b': 'world'}
        e = SampleMultipleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(['a','b']).set_output_field('e').set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['value'], 'helloworld')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_multiple_renamed_field_with_multiple_values_extractor(self):
        doc = { 'a': 'hello', 'b': [{'c': 'world'}, {'c': 'brooklyn'}, {'c': 'new york'}]}
        e = SampleMultipleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(['a','b[*].c']).set_output_field('e').set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['value'], 'helloworld')
        self.assertEqual(updated_doc['e'][1]['value'], 'hellobrooklyn')
        self.assertEqual(updated_doc['e'][2]['value'], 'hellonew york')
        self.assertEqual(updated_doc['a'], 'hello')

    def test_chained_extractor(self):
        
        e1 = SampleSingleRenamedFieldExtractor()
        e2 = SampleMultipleRenamedFieldExtractor()
        e3 = SampleMultipleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a').set_output_field('e').set_extractor(e1)
        ep2 = ExtractorProcessor().set_input_fields(['a','b']).set_output_field('e').set_extractor(e2)
        ep3 = ExtractorProcessor().set_input_fields(['a','b']).set_output_field('e').set_extractor(e2)
        ep4 = ExtractorProcessor().set_input_fields(['a','b']).set_output_field('f').set_extractor(e2)
        doc = { 'a': 'hello', 'b': 'world'}
        updated_doc = execute_processor_chain(doc, [ep1, ep2, ep3, ep4])
        
        self.assertEqual(updated_doc['e'][0]['value'], 'hello')
        self.assertEqual(updated_doc['e'][1]['value'], 'helloworld')
        self.assertEqual(updated_doc['e'][2]['value'], 'helloworld')
        self.assertEqual(updated_doc['f'][0]['value'], 'helloworld')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_chained_extractor_by_processor_inputs(self):
        
        e1 = SampleSingleRenamedFieldExtractor()
        e2 = SampleMultipleRenamedFieldExtractor()
        e3 = SampleMultipleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a').set_output_field('e').set_extractor(e1)
        ep2 = ExtractorProcessor().set_input_fields('b').set_output_field('f').set_extractor(e1)
        ep3 = ExtractorProcessor().set_extractor_processor_inputs(ep2).set_output_field('g').set_extractor(e1).set_name("first")
        ep4 = ExtractorProcessor().set_extractor_processor_inputs([ep1,ep2]).set_output_field('h').set_extractor(e2).set_name("combine")
        ep5 = ExtractorProcessor().set_extractor_processor_inputs(ep3).set_output_field('i').set_extractor(e1).set_name("second")
        ep6 = ExtractorProcessor().set_extractor_processor_inputs(ep5).set_output_field('j').set_extractor(e1).set_name("third")
        ep7 = ExtractorProcessor().set_extractor_processor_inputs(ep4).set_output_field('k').set_extractor(e1)
        doc = { 'a': 'hello', 'b': 'world'}
        updated_doc = execute_processor_chain(doc, [ep1, ep2, ep3, ep4, ep5, ep6, ep7])
        
        self.assertEqual(updated_doc['e'][0]['value'], 'hello')
        self.assertEqual(updated_doc['f'][0]['value'], 'world')
        self.assertEqual(updated_doc['g'][0]['value'], 'world')
        self.assertEqual(updated_doc['h'][0]['value'], 'helloworld')
        self.assertEqual(updated_doc['i'][0]['value'], 'world')
        self.assertEqual(updated_doc['j'][0]['value'], 'world')
        self.assertEqual(updated_doc['k'][0]['value'], 'helloworld')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_outputs_dict_extractor(self):
        doc = { 'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        e2 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a').set_output_fields({'f':'h', 'g':'i'}).set_extractor(e1).set_name("mo")
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep1,'i').set_output_fields('j').set_extractor(e2).set_name("so")
        updated_doc = execute_processor_chain(doc, [ep1, ep2])

        self.assertEqual(updated_doc['h'][0]['value'], 'hello')
        self.assertEqual(updated_doc['h'][0]['original_output_field'], 'f')
        self.assertEqual(updated_doc['i'][0]['value'], 'hello')
        self.assertEqual(updated_doc['i'][0]['original_output_field'], 'g')
        self.assertEqual(updated_doc['j'][0]['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_outputs_list_extractor(self):
        doc = { 'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        e2 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a').set_output_fields(['f', 'g']).set_extractor(e1).set_name("mo")
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep1,'f').set_output_fields('j').set_extractor(e2).set_name("so")
        updated_doc = execute_processor_chain(doc, [ep1, ep2])

        self.assertEqual(updated_doc['f'][0]['value'], 'hello')
        self.assertEqual(updated_doc['g'][0]['value'], 'hello')
        self.assertEqual(updated_doc['j'][0]['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_outputs_empty_extractor(self):
        doc = { 'a': '', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a').set_output_fields(['f', 'g']).set_extractor(e1).set_name("mo")
        updated_doc = execute_processor_chain(doc, [ep1])

        self.assertNotIn('f', updated_doc)
        self.assertNotIn('g', updated_doc)
        self.assertEqual(updated_doc['a'], '')
        self.assertEqual(updated_doc['b'], 'world')

if __name__ == '__main__':
    unittest.main()