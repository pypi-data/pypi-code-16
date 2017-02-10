import unittest
import itertools

from digExtractor.extractor import Extractor
from digExtractor.extractor_processor import ExtractorProcessor
from digExtractor.extractor_processor_chain import execute_processor_chain


class SampleFlatMappedSingleRenamedFieldExtractor(Extractor):

    def __init__(self):
        super(SampleFlatMappedSingleRenamedFieldExtractor, self).__init__()
        self.renamed_input_fields = 'c'

    def extract(self, doc):
        return reduce(lambda x, y: x + y, doc['c'])

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields


class SampleFlatMappedMultipleRenamedFieldExtractor(Extractor):

    def __init__(self):
        super(SampleFlatMappedMultipleRenamedFieldExtractor, self).__init__()
        self.renamed_input_fields = ['c', 'd']

    def extract(self, doc):
        return reduce(lambda x, y: x + y, itertools.chain(doc['c'], doc['d']))

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields

class SampleContextExtractor(Extractor):
    def __init__(self):
        super(SampleContextExtractor, self).__init__()
        self.renamed_input_fields = ['c']
        self.include_context = True

    def extract(self, doc):
        values = doc['c']
        results = list()
        for num, value in enumerate(values):
            if value.startswith("B"):
                results.append(self.wrap_value_with_context(value, 'c',
                                                            num, num + 1))

        return results

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields


class SampleSingleRenamedFieldExtractorArrayConverter(Extractor):

    def __init__(self):
        super(SampleSingleRenamedFieldExtractorArrayConverter, self).__init__()
        self.renamed_input_fields = 'c'

    def extract(self, doc):
        return [['a', 'b']]

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields


class SampleSingleRenamedFieldExtractor(Extractor):

    def __init__(self):
        super(SampleSingleRenamedFieldExtractor, self).__init__()
        self.renamed_input_fields = 'c'

    def extract(self, doc):
        return doc['c']

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields


class SampleMultipleRenamedFieldExtractor(Extractor):

    def __init__(self):
        super(SampleMultipleRenamedFieldExtractor, self).__init__()
        self.renamed_input_fields = ['c', 'd']

    def extract(self, doc):
        return doc['c'] + doc['d']

    def get_metadata(self):
        metadata = dict()
        metadata['extractor'] = "sample"
        return metadata

    def get_renamed_input_fields(self):
        return self.renamed_input_fields


class SampleSingleRenamedFieldMultipleOutputsExtractor(Extractor):

    def __init__(self):
        super(SampleSingleRenamedFieldMultipleOutputsExtractor, self).__init__()
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
        return self.renamed_input_fields


class TestExtractor(unittest.TestCase):

    def test_single_renamed_field_extractor(self):
        doc = {'a': 'hello', 'b': 'world'}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(['a'])\
                                 .set_output_field('e')\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_missing_extractor(self):
        doc = {'b': 'world'}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields('a')\
                                 .set_output_field('e')\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertTrue('e' not in updated_doc)
        self.assertEqual(updated_doc['b'], 'world')

    def test_nested_field_filtered_extractor(self):
        doc = {'a': [{'b': 'world', 'c': 'good'}, {'b': 'cup', 'c': 'bad'}]}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields('a[?c=good].b')\
                                 .set_output_field('e')\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['result']['value'], 'world')

    def test_multiple_renamed_field_extractor(self):
        doc = {'a': 'hello', 'b': 'world'}
        e = SampleMultipleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(['a', 'b'])\
                                 .set_output_field('e')\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_multiple_renamed_field_with_multiple_values_extractor(self):
        doc = {'a': 'hello', 'b': [{'c': 'world'},
                                   {'c': 'brooklyn'},
                                   {'c': 'new york'}]
               }
        e = SampleMultipleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(['a', 'b[*].c'])\
                                 .set_output_field('e')\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)

        self.assertEqual(updated_doc['e'][0]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['e'][1]['result']['value'], 'hellobrooklyn')
        self.assertEqual(updated_doc['e'][2]['result']['value'], 'hellonew york')
        self.assertEqual(updated_doc['a'], 'hello')

    def test_chained_extractor(self):

        e1 = SampleSingleRenamedFieldExtractor()
        e2 = SampleMultipleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_field('e')\
                                  .set_extractor(e1)
        ep2 = ExtractorProcessor().set_input_fields(['a', 'b'])\
                                  .set_output_field('e').set_extractor(e2)
        ep3 = ExtractorProcessor().set_input_fields(['a', 'b'])\
                                  .set_output_field('e')\
                                  .set_extractor(e2)
        ep4 = ExtractorProcessor().set_input_fields(['a', 'b'])\
                                  .set_output_field('f')\
                                  .set_extractor(e2)
        doc = {'a': 'hello', 'b': 'world'}
        updated_doc = execute_processor_chain(doc, [ep1, ep2, ep3, ep4])

        self.assertEqual(updated_doc['e'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['e'][1]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['e'][2]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['f'][0]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_chained_extractor_by_processor_inputs(self):

        e1 = SampleSingleRenamedFieldExtractor()
        e2 = SampleMultipleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_field('e')\
                                  .set_extractor(e1)
        ep2 = ExtractorProcessor().set_input_fields('b')\
                                  .set_output_field('f')\
                                  .set_extractor(e1)
        ep3 = ExtractorProcessor().set_extractor_processor_inputs(ep2)\
                                  .set_output_field('g')\
                                  .set_extractor(e1)\
                                  .set_name("first")
        ep4 = ExtractorProcessor().set_extractor_processor_inputs([ep1, ep2])\
                                  .set_output_field('h')\
                                  .set_extractor(e2)\
                                  .set_name("combine")
        ep5 = ExtractorProcessor().set_extractor_processor_inputs(ep3)\
                                  .set_output_field('i')\
                                  .set_extractor(e1)\
                                  .set_name("second")
        ep6 = ExtractorProcessor().set_extractor_processor_inputs(ep5)\
                                  .set_output_field('j')\
                                  .set_extractor(e1)\
                                  .set_name("third")
        ep7 = ExtractorProcessor().set_extractor_processor_inputs(ep4)\
                                  .set_output_field('k')\
                                  .set_extractor(e1)
        doc = {'a': 'hello', 'b': 'world'}
        updated_doc = execute_processor_chain(doc, [ep1, ep2, ep3, ep4, ep5, ep6, ep7])

        self.assertEqual(updated_doc['e'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['f'][0]['result']['value'], 'world')
        self.assertEqual(updated_doc['g'][0]['result']['value'], 'world')
        self.assertEqual(updated_doc['h'][0]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['i'][0]['result']['value'], 'world')
        self.assertEqual(updated_doc['j'][0]['result']['value'], 'world')
        self.assertEqual(updated_doc['k'][0]['result']['value'], 'helloworld')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_outputs_dict_extractor(self):
        doc = {'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        e2 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields({'f': 'h', 'g': 'i'})\
                                  .set_extractor(e1).set_name("mo")
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep1, 'i')\
                                  .set_output_fields('j')\
                                  .set_extractor(e2).set_name("so")
        updated_doc = execute_processor_chain(doc, [ep1, ep2])

        self.assertEqual(updated_doc['h'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['h'][0]['original_output_field'], 'f')
        self.assertEqual(updated_doc['i'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['i'][0]['original_output_field'], 'g')
        self.assertEqual(updated_doc['j'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_outputs_list_extractor(self):
        doc = {'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        e2 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields(['f', 'g'])\
                                  .set_extractor(e1).set_name("mo")
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep1, 'f')\
                                  .set_output_fields('j')\
                                  .set_extractor(e2).set_name("so")
        updated_doc = execute_processor_chain(doc, [ep1, ep2])

        self.assertEqual(updated_doc['f'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['g'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['j'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_outputs_empty_extractor(self):
        doc = {'a': '', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields(['f', 'g'])\
                                  .set_extractor(e1).set_name("mo")
        updated_doc = execute_processor_chain(doc, [ep1])

        self.assertNotIn('f', updated_doc)
        self.assertNotIn('g', updated_doc)
        self.assertEqual(updated_doc['a'], '')
        self.assertEqual(updated_doc['b'], 'world')

    def test_context_extractor(self):
        doc = {'a': '', 'b': ['borscht', 'Bourne', 'barn', 'Block']}
        e1 = SampleContextExtractor()
        ep1 = ExtractorProcessor().set_input_fields('b')\
                                  .set_output_fields('f')\
                                  .set_extractor(e1).set_name("mo")
        updated_doc = execute_processor_chain(doc, [ep1])

        self.assertEqual(updated_doc['f'][0]['result'][0]['value'], 'Bourne')
        self.assertEqual(updated_doc['f'][0]['result'][0]['context']['start'], 1)
        self.assertEqual(updated_doc['f'][0]['result'][0]['context']['end'], 2)
        self.assertEqual(updated_doc['f'][0]['result'][1]['value'], 'Block')
        self.assertEqual(updated_doc['f'][0]['result'][1]['context']['start'], 3)
        self.assertEqual(updated_doc['f'][0]['result'][1]['context']['end'], 4)
        self.assertEqual(updated_doc['a'], '')
        self.assertEqual(updated_doc['b'], ['borscht', 'Bourne', 'barn', 'Block'])

    def test_array_extractor(self):
        doc = { 'a': 'my name is foo', 'b': 'world'}
        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields('a')\
                                 .set_output_fields('g')\
                                 .set_extractor(e).set_name("no")
        updated_doc = ep.extract(doc)
        e2 = SampleSingleRenamedFieldExtractorArrayConverter()
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep)\
                                  .set_output_field('e')\
                                  .set_extractor(e2)\
                                  .set_name("oo")
        updated_doc = ep2.extract(updated_doc)
        ep3 = ExtractorProcessor().set_extractor_processor_inputs(ep)\
                                  .set_output_fields('e')\
                                  .set_extractor(e).set_name("po")
        updated_doc = ep3.extract(doc)

    def test_single_renamed_field_nested_outputs_list_extractor(self):
        doc = {'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldExtractor()
        e2 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields('f.a')\
                                  .set_extractor(e1).set_name("mo")
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep1)\
                                  .set_output_fields('j.a')\
                                  .set_extractor(e2).set_name("so")
        updated_doc = execute_processor_chain(doc, [ep1, ep2, ep1])

        self.assertEqual(updated_doc['f']['a'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['f']['a'][1]['result']['value'], 'hello')
        self.assertEqual(updated_doc['j']['a'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_renamed_field_multiple_nested_outputs_list_extractor(self):
        doc = {'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldMultipleOutputsExtractor()
        e2 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields({'f': 'f.a', 'g': 'g.a'})\
                                  .set_extractor(e1).set_name("mo")
        ep2 = ExtractorProcessor().set_extractor_processor_inputs(ep1, 'f.a')\
                                  .set_output_fields('j.a')\
                                  .set_extractor(e2).set_name("so")
        updated_doc = execute_processor_chain(doc, [ep1, ep2])

        self.assertEqual(updated_doc['f']['a'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['g']['a'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['j']['a'][0]['result']['value'], 'hello')
        self.assertEqual(updated_doc['a'], 'hello')
        self.assertEqual(updated_doc['b'], 'world')

    def test_single_input_matching_multiple_extractions(self):
        doc = {'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields('hp.word')\
                                  .set_extractor(e1).set_name("h")
        e2 = SampleFlatMappedSingleRenamedFieldExtractor()
        ep2 = ExtractorProcessor().set_input_fields(['hp.word[*].result.value'])\
                                  .set_output_fields('hhhhh.word')\
                                  .set_extractor(e2).set_name("m")\
                                  .set_flat_map_inputs(True)
        updated_doc = execute_processor_chain(doc, [ep1, ep1, ep2])
        self.assertEqual(updated_doc['hhhhh']['word'][0]['result']['value'],
                         "hellohello")

    def test_multiple_inputs_matching_multiple_extractions(self):
        doc = {'a': 'hello', 'b': 'world'}
        e1 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields('hp.word')\
                                  .set_extractor(e1).set_name("h")
        ep2 = ExtractorProcessor().set_input_fields('b')\
                                  .set_output_fields('hr.word')\
                                  .set_extractor(e1).set_name("w")
        e2 = SampleFlatMappedMultipleRenamedFieldExtractor()
        ep3 = ExtractorProcessor().set_input_fields(['hp.word[*].result.value',
                                                     'hr.word[*].result.value'])\
                                  .set_output_fields('hhhhh.word')\
                                  .set_extractor(e2).set_name("m")\
                                  .set_flat_map_inputs(True)
        updated_doc = execute_processor_chain(doc, [ep1, ep1, ep2, ep2, ep3])
        self.assertEqual(updated_doc['hhhhh']['word'][0]['result']['value'],
                         "hellohelloworldworld")

    def test_multiple_list_inputs_matching_multiple_extractions(self):
        doc = {'a': ['hello', 'goodbye'], 'b': ['world', 'cup']}
        e1 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields('hp.word')\
                                  .set_extractor(e1).set_name("h")
        ep2 = ExtractorProcessor().set_input_fields('b')\
                                  .set_output_fields('hr.word')\
                                  .set_extractor(e1).set_name("w")
        e2 = SampleFlatMappedMultipleRenamedFieldExtractor()
        ep3 = ExtractorProcessor().set_input_fields(['hp.word[*].result[*][value]',
                                                     'hr.word[*].result[*][value]'])\
                                  .set_output_fields('hhhhh.word')\
                                  .set_extractor(e2).set_name("m")\
                                  .set_flat_map_inputs(True)
        ep4 = ExtractorProcessor().set_input_fields(['a',
                                                     'b'])\
                                  .set_output_fields('iiiii.word')\
                                  .set_extractor(e2).set_name("m")\
                                  .set_flat_map_inputs(True)
        updated_doc = execute_processor_chain(doc, [ep1, ep1, ep2, ep2])
        updated_doc = execute_processor_chain(updated_doc, [ep3, ep4])
        self.assertEqual(updated_doc['hhhhh']['word'][0]['result']['value'],
                         "hellogoodbyehellogoodbyeworldcupworldcup")
        self.assertEqual(updated_doc['iiiii']['word'][0]['result']['value'],
                         "hellogoodbyeworldcup")

    def test_multiple_list_inputs_matching_multiple_extractions_unioned(self):
        doc = {'a': ['hello', 'goodbye'], 'b': ['world', 'cup']}
        e1 = SampleSingleRenamedFieldExtractor()
        ep1 = ExtractorProcessor().set_input_fields('a')\
                                  .set_output_fields('hp.word')\
                                  .set_extractor(e1).set_name("h")
        ep2 = ExtractorProcessor().set_input_fields('b')\
                                  .set_output_fields('hr.word')\
                                  .set_extractor(e1).set_name("w")
        e2 = SampleFlatMappedSingleRenamedFieldExtractor()
        ep3 = ExtractorProcessor().set_extractor_processor_inputs([[ep1,
                                                                    ep2]])\
                                  .set_output_fields('hhhhh.word')\
                                  .set_extractor(e2).set_name("m")\
                                  .set_flat_map_inputs(True)
        updated_doc = execute_processor_chain(doc, [ep1, ep2])
        updated_doc = execute_processor_chain(updated_doc, [ep3])
        self.assertEqual(updated_doc['hhhhh']['word'][0]['result']['value'],
                         "hellogoodbyeworldcup")
        e3 = SampleFlatMappedMultipleRenamedFieldExtractor()
        ep4 = ExtractorProcessor().set_extractor_processor_inputs([[ep1, ep3],
                                                                   [ep2, ep3]])\
                                  .set_output_fields('iiiii.word')\
                                  .set_extractor(e3).set_name("m")\
                                  .set_flat_map_inputs(True)
        updated_doc = execute_processor_chain(updated_doc, [ep4])
        self.assertEqual(updated_doc['iiiii']['word'][0]['result']['value'],
                         "hellogoodbyehellogoodbyeworldcupworldcuphellogoodbyeworldcup")
        ep5 = ExtractorProcessor().set_extractor_processor_inputs([[ep1,
                                                                    ep2,
                                                                    ep1,
                                                                    ep2]])\
                                  .set_output_fields('jjjjj.word')\
                                  .set_extractor(e2).set_name("m")\
                                  .set_flat_map_inputs(True)
        updated_doc = execute_processor_chain(updated_doc, [ep5])
        self.assertEqual(updated_doc['jjjjj']['word'][0]['result']['value'],
                         "hellogoodbyeworldcuphellogoodbyeworldcup")


    def test_jsonpath_bracket_notation_update_extractor(self):
        doc = {"a": "hello", "b": [{"b1": [{"b11": "world"}, {"b12": "world"}]}, {"b2": "world"}]}
        input_field = 'b.[0].[b1].[1].b12'
        output_field = 'b.[0].[b1].[1].text'

        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(input_field)\
                                 .set_output_field(output_field)\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)
        self.assertEqual(updated_doc['b'][0]['b1'][1]['text'][0]['result']['value'], 'world')


    def test_jsonpath_alternate_bracket_notation_update_extractor(self):
        doc = {"a": "hello", "b": [{"b1": [{"b11": "world"}, {"b12": "world"}]}, {"b2": "world"}]}
        input_field = 'b[0][b1][1].b12'
        output_field = 'b[0][b1][1].text'

        e = SampleSingleRenamedFieldExtractor()
        ep = ExtractorProcessor().set_input_fields(input_field)\
                                 .set_output_field(output_field)\
                                 .set_extractor(e)
        updated_doc = ep.extract(doc)
        self.assertEqual(updated_doc['b'][0]['b1'][1]['text'][0]['result']['value'], 'world')


if __name__ == '__main__':
    unittest.main()
