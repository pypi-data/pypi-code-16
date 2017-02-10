# -*- coding: utf-8 -*-
"""Module for defining an extractor that accepts a list of tokens
and outputs tokens that exist in a user provided trie"""
import copy

from digExtractor.extractor import Extractor
from landmark_extractor.extraction.Landmark import Rule, RuleSet
from landmark_extractor.extraction.Landmark import flattenResult


class DigMultiplexingLandmarkExtractor(Extractor):

    def __init__(self):
        self.renamed_input_fields = ['html', 'selector']
        self.extractors = None
        self.selector_function = lambda x: x

    def get_extractors(self):
        return self.extractors

    def set_extractors(self, extractors):
        if not isinstance(extractors, dict):
            raise ValueError("extractors must be a dict")
        self.extractors = extractors
        return self

    def get_selector_function(self):
        return self.selector_function

    def set_selector_function(self, selector_function):
        self.selector_function = selector_function
        return self

    def extract(self, doc):
        if "selector" in doc:
            selector_value = self.selector_function(doc["selector"])
            if selector_value in self.extractors:
                extracted = self.extractors[selector_value].extract(doc)
                return extracted

    def get_metadata(self):
        """Returns a copy of the metadata that characterizes this extractor"""
        return copy.copy(self.metadata)

    def set_metadata(self, metadata):
        """Overwrite the metadata that characterizes this extractor"""
        self.metadata = metadata
        return self

    def get_renamed_input_fields(self):
        """Return a scalar or ordered list of fields to rename to"""
        return self.renamed_input_fields
