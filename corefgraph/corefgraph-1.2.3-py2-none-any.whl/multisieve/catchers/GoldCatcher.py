# coding=utf-8
""" Catcher for retrieve valid constituent mentions for the system."""

from corefgraph.multisieve.catchers.baseCatcher import BaseCatcher
from corefgraph.constants import ID, FORM

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class GoldCatcher(BaseCatcher):
    """ Class that catch Gold mentions."""

    short_name = "GoldCatcher"

    def __init__(self, graph_builder, extractor):
        BaseCatcher.__init__(self, graph_builder, extractor)
        self.logger.warning("Gold catcher Active")

    def catch_mention(self, mention_candidate):
        """ check if the mention is in gold mention dict.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """
        mention_id = mention_candidate[ID]
        if mention_id in self.extractor.gold_mentions_by_constituent:
            for gold_mention in \
                    self.extractor.gold_mentions_by_constituent.pop(mention_id):
                self.extractor.add_mention(mention=gold_mention)
                self.extractor.logger.debug(
                    "Mention accepted: -%s- -%s- Gold MENTION",
                    gold_mention[FORM],
                    gold_mention[ID])
        return
