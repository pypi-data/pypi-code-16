# -*- coding: utf-8 -*-
"""Module for defining an extractor that accepts a list of tokens
and outputs tokens that exist in a user provided trie"""
import copy
import json
import re

from digExtractor.extractor import Extractor
from landmark_extractor.extraction.Landmark import Rule, RuleSet


class DigLandmarkExtractor(Extractor):

    rule_name_regex = r'-[\d]+$'

    def __init__(self):
        self.renamed_input_fields = 'html'
        self.rule = None
        self.rule_set = None
        self.minimum_pct_rules = 0.5

    def get_minimum_pct_rules(self):
        self.minimum_pct_rules

    def set_minimum_pct_rules(self, minimum_pct_rules):
        self.minimum_pct_rules = minimum_pct_rules
        return self

    def get_rule(self):
        return self.rule

    def set_rule(self, rule):
        if not isinstance(rule, Rule):
            raise ValueError("rule must be a Rule")
        self.rule = rule
        return self

    def get_rule_set(self):
        return self.rule_set

    def set_rule_set(self, rule_set):
        if not isinstance(rule_set, RuleSet):
            raise ValueError("rule_set must be a RuleSet")
        self.rule_set = RuleSet(json.loads(rule_set.toJson()))
        self.rule_set.rules = [rule for rule in self.rule_set.rules
                               if not rule.name.startswith("junk")]
        return self

    def get_trimmed_rule_names(self):
        if self.rule:
            return re.sub(self.rule_name_regex, "", self.rule.name)
        elif self.rule_set:
            return [re.sub(self.rule_name_regex, "", rule.name)
                    for rule in self.rule_set.rules]

    def flattenResult(self, extraction_object, name='root'):
        result = {}
        if isinstance(extraction_object, dict):
            if 'sub_rules' in extraction_object:
                for item in extraction_object['sub_rules']:
                    result[item] = self.flattenResult(extraction_object['sub_rules'][item], item)
            elif 'sequence' in extraction_object:
                result = self.flattenResult(extraction_object['sequence'], 'sequence')
            elif 'extract' in extraction_object:
                if self.get_include_context():
                    return self.convert_result(extraction_object)
                else:
                    return extraction_object['extract']
            else:
                for extract in extraction_object:
                    result[extract] = self.flattenResult(extraction_object[extract], extract)

        if isinstance(extraction_object, list):
            result = []
            for extract in extraction_object:
                result.append(self.flattenResult(extract, 'sequence'))
        return result

    def convert_result(self, result):
        if not result['extract']:
            return ""
        return self.wrap_value_with_context(result['extract'],
                                            'html',
                                            result['begin_index'],
                                            result['end_index'])

    def extract(self, doc):
        if self.rule is not None:
            html = doc['html']
            result = self.rule.apply(html)
            result = self.flattenResult(result)
            return result
        elif self.rule_set is not None:
            result = dict()
            html = doc['html']
            hits = 0
            for rule in self.rule_set.rules:
                rule_name_trimmed = re.sub(self.rule_name_regex,
                                           "", rule.name)
                rule_result = rule.apply(html)
                rule_result = self.flattenResult(rule_result)
                if rule_result:
                    hits += 1
                    if rule_name_trimmed not in result:
                        result[rule_name_trimmed] = rule_result
                    elif isinstance(result[rule_name_trimmed], list):
                        result[rule_name_trimmed].append(rule_result)
                    else:
                        result[rule_name_trimmed] =\
                            [result[rule_name_trimmed], rule_result]
            if hits < len(self.rule_set.rules) * self.minimum_pct_rules:
                result = {}

            return result

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
