# -*- coding: utf-8 -*-
# @Author: ZwEin
# @Date:   2016-10-03 23:46:09
# @Last Modified by:   ZwEin
# @Last Modified time: 2016-10-05 10:39:44

import copy
from digExtractor.extractor import Extractor
from date_manipulation import DataManipulation


class PostingDateExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = ['text']

    def extract(self, doc):
        if 'text' in doc:
            return DataManipulation.date_created(doc['text'], None,
                                                 'date')
        return None

    def get_metadata(self):
        return copy.copy(self.metadata)

    def set_metadata(self, metadata):
        self.metadata = metadata
        return self

    def get_renamed_input_fields(self):
        return self.renamed_input_fields
