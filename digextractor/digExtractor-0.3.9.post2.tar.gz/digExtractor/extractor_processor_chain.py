# -*- coding: utf-8 -*-
"""This module defines a method for applying extractor processors to a doc"""

def execute_processor_chain(doc, processors):
    """Applies a sequence of ExtractorProcessors which wrap Extractors
    to a doc which will then contain all the extracted values"""
    return reduce(__processor_chain_reducer, iter(processors), doc)


def __processor_chain_reducer(doc, processor):
    """Calling ExtractorProcessor extract on doc returns a document with
    extracted value from the Extractor it wraps"""
    return processor.extract(doc)
