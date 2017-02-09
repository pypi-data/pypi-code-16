# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-06-21 12:36:47
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-12-07 12:45:13

import copy
import types
from digExtractor.extractor import Extractor
from pnmatcher import PhoneNumberMatcher


class PhoneExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = 'input'
        self.extractor = PhoneNumberMatcher(_output_format='obfuscation')

    def extract(self, doc):
        extracts = []
        extracts += self.extractor.match(doc['input'],
                                         source_type=self.get_source_type(),
                                         include_context=self.get_include_context())
        return extracts

    def get_metadata(self):
        return copy.copy(self.metadata)

    def set_metadata(self, metadata):
        self.metadata = metadata
        return self

    def get_renamed_input_fields(self):
        return self.renamed_input_fields

    def set_renamed_input_fields(self, renamed_input_fields):
        if not (isinstance(renamed_input_fields, basestring) or
           isinstance(renamed_input_fields, types.ListType)):
            raise ValueError("renamed_input_fields must be a string or a list")
        self.renamed_input_fields = renamed_input_fields
        return self

    def get_source_type(self):
        return self.source_type

    def set_source_type(self, source_type):
        self.source_type = source_type
        return self
