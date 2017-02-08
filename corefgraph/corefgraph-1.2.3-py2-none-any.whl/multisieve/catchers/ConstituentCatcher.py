# coding=utf-8
""" Catcher for retrieve constituent mentions for the system."""

from .baseCatcher import BaseCatcher
from corefgraph.resources.tagset import constituent_tags
from corefgraph.constants import TAG, FORM, SPAN

__author__ = "Josu Bermudez <josu.bermudez@deusto.es>"


class ConstituentCatcher(BaseCatcher):
    """ Class that catch mentions that are NPs."""

    short_name = "ConstituentCatcher"

    def catch_mention(self, mention_candidate):
        """ check if the mention is a valid constituent.

        :param mention_candidate : The mention candidate to test.
        :return: True or False.
        """
        # if mention_candidate[SPAN] in self.extractor.candidates_span:
        #     return False
        if self._inside_ne(mention_candidate[SPAN]):
            return False

        mention_tag = mention_candidate.get(TAG)
        if constituent_tags.mention_constituents(mention_tag):
            self.logger.debug(
                "Mention is valid constituent: %s", mention_candidate[FORM])
            return True
        return False


class PermissiveConstituentCatcher(ConstituentCatcher):
    """ Class that catch mentions that are NPs."""

    short_name = "PermissiveConstituentCatcher"
    soft_ne = True
