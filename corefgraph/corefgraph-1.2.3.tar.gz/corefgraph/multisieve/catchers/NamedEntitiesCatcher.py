# coding=utf-8
""" Catcher for retrieve named entities as mentions for the system."""

from corefgraph.multisieve.catchers.baseCatcher import BaseCatcher
from corefgraph.constants import NER, SPAN
from corefgraph.resources.tagset import ner_tags

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class NamedEntitiesCatcher(BaseCatcher):
    """ Catcher of Named entities mentions."""

    short_name = "NamedEntitiesCatcher"

    def catch_mention(self, mention_candidate):
        """ check if the mention is in named Entity mention dict.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """
        # if mention_candidate[SPAN] in self.extractor.candidates_span:
        #     return False

        if ner_tags.mention_ner(mention_candidate.get(NER)):
            return True

        return False
