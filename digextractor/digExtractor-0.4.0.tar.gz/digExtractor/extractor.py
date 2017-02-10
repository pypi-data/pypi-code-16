# -*- coding: utf-8 -*-
"""This module defines the API for the Extractor class"""
from types import ListType

class Extractor(object):
    """An abstract class that defines the expected methods that need to be
    implemented for an extractor to be included in a pipeline"""

    def __init__(self):
        self.renamed_input_fields = list()
        self.include_context = False

    def extract(self, doc):
        """This method accepts a document and computes a value based on
        the fields in the document as defined by 'self.renamed_input_fields'"""
        raise NotImplementedError("Need to implement extract function")

    # should create a new dictionary each time
    def get_metadata(self):
        """This method returns a dictionary that characterizes the extractor"""
        raise NotImplementedError("Need to implement get_metadata function")

    def set_metadata(self, metadata):
        """This method expects a dictionary that characterizes the extractor.
        At a minimum, it should have the 'extractor' field set with a name
        for the extractor, along with any additional configuration options
        for the extractor."""
        raise NotImplementedError("Need to implement set_metadata function")

    def get_renamed_input_fields(self):
        """Returns a scalar or ordered list of input fields expected
        by the extract function in the document passed to 'extract'"""
        raise NotImplementedError(
            "Need to implement get_renamed_input_fields function")

    def set_renamed_input_fields(self, renamed_input_fields):
        """This method expects a scalar string or a list of input_fields
        to """
        if not (isinstance(renamed_input_fields, basestring) or
                isinstance(renamed_input_fields, ListType)):
            raise ValueError("renamed_input_fields must be a string or a list")
        self.renamed_input_fields = renamed_input_fields
        return self

    def set_include_context(self, include_context):
        self.include_context = include_context
        return self

    def get_include_context(self):
        if not hasattr(self, "include_context"):
            return False
        return self.include_context

    def wrap_value_with_context(self, value, field, start, end):
        return {'value': value,
                'context': {'field': field,
                            'start': start,
                            'end': end
                            }
                }
