# -*- coding: utf-8 -*-
"""This module defines the API for the ExtractorProcessor class"""
import itertools
import types
import re
from jsonpath_rw.jsonpath import JSONPath
from jsonpath_rw_ext import parse


class ExtractorProcessor(object):
    """This class wraps an Extractor.  It takes a document,
    pulls out the inputs defined by the input_fields or the
    ExtractorProcessor inputs, and creates a new document with
    standardized names as defined by the extractors renamed input
    fields.  It takes the output of the extractor along with a copy
    of the metadata for the extractor and inserts it into the document"""

    def __init__(self):
        self.output_field = None
        self.output_fields = None
        self.input_fields = None
        self.jsonpaths = None
        self.extractor = None
        self.name = None
        self.flat_map_inputs = False

    def set_flat_map_inputs(self, flat_map_inputs):
        self.flat_map_inputs = flat_map_inputs
        return self

    def set_name(self, name):
        """Sets a name for the ExtractorProcessor"""
        self.name = name
        return self

    def get_name(self):
        """Gets the ExtractorProcessor name"""
        return self.name

    def set_output_field(self, output_field):
        """Defines where to put the output of the extractor in the doc"""
        self.output_field = output_field
        return self

    def set_output_fields(self, output_fields):
        """Defines where to put the dictionary output of the extractor in the doc, but renames
        the fields of the extracted output for the document or just filters the keys"""
        if isinstance(output_fields, dict) or isinstance(output_fields, list):
            self.output_fields = output_fields
        elif isinstance(output_fields, basestring):
            self.output_field = output_fields
        else:
            raise ValueError("set_output_fields requires a dictionary of "
                             + "output fields to remap, a list of keys to filter, or a scalar string")
        return self

    def __get_jp(self, extractor_processor, sub_output=None):
        """Tries to get name from ExtractorProcessor to filter on first.
        Otherwise falls back to filtering based on its metadata"""
        if sub_output is None and extractor_processor.output_field is None:
            raise ValueError(
                "ExtractorProcessors input paths cannot be unioned across fields.  Please specify either a sub_output or use a single scalar output_field")
        if extractor_processor.get_output_jsonpath_with_name(sub_output) is not None:
            return extractor_processor.get_output_jsonpath_with_name(sub_output)
        else:
            return extractor_processor.get_output_jsonpath(sub_output)

    def set_extractor_processor_inputs(self, extractor_processors,
                                       sub_output=None):
        """Instead of specifying fields in the source document to rename
        for the extractor, allows the user to specify ExtractorProcessors that
        are executed earlier in the chain and generate json paths from
        their output fields"""
        if not (isinstance(extractor_processors, ExtractorProcessor) or
                isinstance(extractor_processors, types.ListType)):
            raise ValueError(
                "extractor_processors must be an ExtractorProcessor or a list")

        if isinstance(extractor_processors, ExtractorProcessor):
            extractor_processor = extractor_processors
            self.input_fields = self.__get_jp(extractor_processor, sub_output)
        elif isinstance(extractor_processors, types.ListType):
            self.input_fields = list()
            for extractor_processor in extractor_processors:
                if isinstance(extractor_processor, ExtractorProcessor):
                    self.input_fields.append(
                        self.__get_jp(extractor_processor, sub_output))
                elif isinstance(extractor_processor, list):
                    self.input_fields.append(
                        reduce(lambda a, b: "{}|{}".format(a, b),
                               ["({})".format(self.__get_jp(x, sub_output))
                                for x in extractor_processor]))

        self.generate_json_paths()
        return self

    def get_output_jsonpath_field(self, sub_output=None):
        """attempts to create an output jsonpath from a particular ouput field"""
        if sub_output is not None:
            if self.output_fields is None or\
                (isinstance(self.output_fields, dict) and not sub_output in self.output_fields.itervalues()) or\
                    (isinstance(self.output_fields, list) and not sub_output in self.output_fields):
                raise ValueError(
                    "Cannot generate output jsonpath because this ExtractorProcessor will not output {}".format(sub_output))
            output_jsonpath_field = sub_output
        else:
            output_jsonpath_field = self.output_field
        return output_jsonpath_field

    def get_output_jsonpath_with_name(self, sub_output=None):
        """If ExtractorProcessor has a name defined, return
        a JSONPath that has a filter on that name"""
        if self.name is None:
            return None

        output_jsonpath_field = self.get_output_jsonpath_field(sub_output)
        extractor_filter = "name='{}'".format(self.name)
        output_jsonpath = "{}[?{}].(result[*][value])".format(
            output_jsonpath_field, extractor_filter)

        return output_jsonpath

    def get_output_jsonpath(self, sub_output=None):
        """Attempt to build a JSONPath filter for this ExtractorProcessor
        that captures how to get at the outputs of the wrapped Extractor"""
        output_jsonpath_field = self.get_output_jsonpath_field(sub_output)

        metadata = self.extractor.get_metadata()
        metadata['source'] = str(self.input_fields)
        extractor_filter = ""
        is_first = True
        for key, value in metadata.iteritems():
            if is_first:
                is_first = False
            else:
                extractor_filter = extractor_filter + " & "

            if isinstance(value, basestring):
                extractor_filter = extractor_filter\
                    + "{}=\"{}\"".format(key,
                                         re.sub('(?<=[^\\\])\"', "'", value))
            elif isinstance(value, types.ListType):
                extractor_filter = extractor_filter\
                    + "{}={}".format(key, str(value))
        output_jsonpath = "{}[?{}].result.value".format(
            output_jsonpath_field, extractor_filter)

        return output_jsonpath

    def set_input_fields(self, input_fields):
        """Given a scalar or ordered list of strings generate JSONPaths
        that describe how to access the values necessary for the Extractor """
        if not (isinstance(input_fields, basestring) or
                isinstance(input_fields, types.ListType)):
            raise ValueError("input_fields must be a string or a list")
        self.input_fields = input_fields
        self.generate_json_paths()
        return self

    def generate_json_paths(self):
        """Given a scalar or ordered list of strings parse them to
        generate JSONPaths"""
        if isinstance(self.input_fields, basestring):
            try:
                self.jsonpaths = parse(self.input_fields)
            except Exception as exception:
                print "input_fields failed {}".format(self.input_fields)
                raise exception

        elif isinstance(self.input_fields, types.ListType):
            self.jsonpaths = list()
            for input_field in self.input_fields:
                self.jsonpaths.append(parse(input_field))
            if len(self.jsonpaths) == 1:
                self.jsonpaths = self.jsonpaths[0]

    def set_extractor(self, extractor):
        """Set the Extractor for the ExtractorProcessor to wrap"""
        self.extractor = extractor
        return self

    def get_extractor(self):
        """Get the Extractor wrapped by ExtractorProcessor"""
        return self.extractor

    def insert_extracted_value(self, doc, extracted_value,
                               output_field, original_output_field=None):
        """inserts the extracted value into doc at the field specified 
        by output_field"""
        if not extracted_value:
            return doc
        metadata = self.extractor.get_metadata()
        if not self.extractor.get_include_context():
            if isinstance(extracted_value, list):
                result = list()
                for ev in extracted_value:
                    result.append({'value': ev})
            else:
                result = {'value': extracted_value}
        else:
            result = extracted_value
        metadata['result'] = result
        metadata['source'] = str(self.input_fields)

        if original_output_field is not None:
            metadata['original_output_field'] = original_output_field

        if self.name is not None:
            metadata['name'] = self.name

        field_elements = output_field.split('.')
        while len(field_elements) > 1:
            field_element = field_elements.pop(0)
            if '[' in field_element:
                if not field_element.startswith('['):
                    array_field_elements = field_element.split('[', 1)
                    array_field_element = array_field_elements[0]
                    doc = doc[array_field_element]
                    field_element = array_field_elements[1]
                array_elements = field_element.split(']')
                for array_element in array_elements:
                    if not array_element:
                        continue
                    if array_element.startswith('['):
                        array_element = array_element[1:]
                    if array_element.isdigit() and isinstance(doc, list):
                        doc = doc[int(array_element)]
                    else:
                        doc = doc[array_element]
            else:
                if field_element not in doc:
                    doc[field_element] = {}
                doc = doc[field_element]
        field_element = field_elements[0]
        if field_element in doc:
            output = doc[field_element]
            if isinstance(output, dict):
                output = [output, metadata]
            elif isinstance(output, types.ListType):
                output.append(metadata)

        else:
            output = [metadata]
        doc[field_element] = output

    def extract_from_renamed_inputs(self, doc, renamed_inputs):
        """Apply the extractor to a document containing the renamed_inputs
        and insert the resulting value if defined in the value field
        of a copy of the extractor's metadata and insert that into the doc"""
        extracted_value = self.extractor.extract(renamed_inputs)
        if not extracted_value:
            return doc

        if self.output_fields is not None and isinstance(extracted_value, dict):
            if isinstance(self.output_fields, list):
                for field in self.output_fields:
                    if field in extracted_value:
                        self.insert_extracted_value(
                            doc, extracted_value[field], field)
            elif isinstance(self.output_fields, dict):
                for key, value in self.output_fields.iteritems():
                    if key in extracted_value:
                        self.insert_extracted_value(
                            doc, extracted_value[key], value, key)
        else:
            self.insert_extracted_value(
                doc, extracted_value, self.output_field)

    @staticmethod
    def add_tuple_to_doc(doc, tup):
        """Splits up a tuple and inserts its elements as a key value pair"""
        doc[tup[0]] = tup[1]
        return doc


    def extract(self, doc):
        """From the defined JSONPath(s), pull out the values and
        insert them into a document with renamed field(s) then
        apply the Extractor and return the doc with the extracted values  """
        if isinstance(self.jsonpaths, JSONPath):
            input_field = self.extractor.get_renamed_input_fields()
            if isinstance(self.extractor.get_renamed_input_fields(), list):
                input_field = input_field[0]

            jsonpath = self.jsonpaths
            renamed_inputs = dict()
            if self.flat_map_inputs:
                flat_mapped = itertools.chain.from_iterable(
                    [iter(match.value)
                     if hasattr(match.value, '__iter__') and
                     not isinstance(match.value, dict) and
                     not isinstance(match.value, basestring)
                     else iter([match.value])
                     for match in jsonpath.find(doc)])
                renamed_inputs[input_field] = flat_mapped
                if input_field in renamed_inputs:
                    self.extract_from_renamed_inputs(doc, renamed_inputs)

            else:
                for value in [match.value for match in jsonpath.find(doc)]:
                    renamed_inputs[input_field] = value
                    self.extract_from_renamed_inputs(doc, renamed_inputs)

        elif isinstance(self.jsonpaths, types.ListType):

            renamed_inputs_lists = dict()
            for jsonpath, renamed_input in \
                    itertools.izip(
                    iter(self.jsonpaths),
                    iter(self.extractor.get_renamed_input_fields())):
                renamed_inputs_lists[renamed_input] = [
                    match.value for match in jsonpath.find(doc)]

            if self.flat_map_inputs:
                renamed_inputs_tuple_lists = [
                    (x, itertools.chain.from_iterable(
                        [iter(z) if hasattr(z, '__iter__') and
                         not isinstance(z, dict) and
                         not isinstance(z, basestring)
                         else iter([z])for z in y]))
                    for x, y in renamed_inputs_lists.iteritems()]
                renamed_inputs = reduce(
                    ExtractorProcessor.add_tuple_to_doc,
                    renamed_inputs_tuple_lists, dict())
                self.extract_from_renamed_inputs(doc, renamed_inputs)
            else:
                renamed_inputs_lists_lists = [[(x, z) for z in y]
                                              for x, y in
                                              renamed_inputs_lists.iteritems()]
                for i in itertools.product(*renamed_inputs_lists_lists):
                    renamed_inputs = reduce(
                        ExtractorProcessor.add_tuple_to_doc, i, dict())
                    self.extract_from_renamed_inputs(doc, renamed_inputs)
        else:
            raise ValueError("input_fields must be a string or a list")

        return doc
