# coding=utf-8
""" This module contains the primary infrastructure and the entry point class
for usage the module.

"""
from corefgraph.multisieve.extractor import SentenceCandidateExtractor
from . import sieves
from corefgraph.constants import SPAN, ID, FORM
from purges import purges_by_name
from logging import getLogger


__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'
__date__ = '14-11-2012'


class MultiSieveProcessor:
    """A coreference detector based on the lee et all. 2013 multi sieve system
    of Stanford University.
    """
    logger = getLogger(__name__)

    def __init__(self, sieves_list):
        self.links = []
        self.logger.info("Sieves: %s", sieves_list)
        self.sieves = self.load_sieves(sieves_list)

    def get_meta(self):
        meta = {}
        for sieve in self.sieves:
            meta[sieve.short_name] = sieve.get_meta()
        return meta

    def process(self, graph_builder, mentions_text_order, mentions_candidate_order):
        """ Process a candidate cluster list thought the sieves using the output
         of the each sieve as input of the next.
        """
        sieve_output = {}
        for sentence in mentions_text_order:
            for mention in sentence:
                entity = (mention[SPAN], [mention, ])
                mention["entity"] = entity
                # backup output
                sieve_output[mention[SPAN]] = [mention, ]
        for sieve in self.sieves:
            sieve_output = sieve.resolve(
                graph_builder=graph_builder,
                mentions_textual_order=mentions_text_order,
                mentions_candidate_order=mentions_candidate_order)

        return [sieve_output[key] for key in sorted(sieve_output.keys())]

    def load_sieves(self, sieves_list):
        """ Load the sieves from a list of string. The id of the sieves to load
         is its short name.

        :param sieves_list: A list of string containing the short name of the
            strings to load.

        :return: A list of ready to use sieve objects.
        """
        return [
            sieves.sieves_by_name[sieve_class]()
            for sieve_class in sieves_list]


class CoreferenceProcessor:
    """ Detect chunks or word of a graph as coreferent with each others.
    """

    logger = getLogger(__name__)

    local_mentions_constant = "LOCAL_MENTIONS"
    soft_purge_constant = "SOFT_PURGES"
    soft_filter_constant = "SOFT_FILTERS"

    def __init__(self,
                 graph_builder,
                 extractor_options,
                 sieves_list,
                 mention_catchers,
                 mention_filters,
                 mention_purges
                 ):

        self.graph_builder = graph_builder

        self.purges = self.load_purges(mention_purges)
        if self.soft_filter_constant in extractor_options:
            self.logger.info("Filters in soft mode")
            self.soft_filters = True
        else:
            self.soft_filters = False

        if self.soft_purge_constant in extractor_options:
            self.logger.info("Purges in soft mode")
            self.soft_purges = True
        else:
            self.soft_purges = False

        self.candidate_extractor = SentenceCandidateExtractor(
            graph_builder=self.graph_builder,
            mention_catchers=mention_catchers,
            mention_filters=mention_filters,
            soft_filter=self.soft_filters
        )
        self.multi_sieve = MultiSieveProcessor(
            sieves_list=sieves_list
        )
        self.mentions_textual_order = []
        # self.mentions_constituent_order = []
        self.mentions_candidate_order = []
        # self.mentions = []
        # self.candidates_per_mention = dict()
        self.coreference_proposal = []
        self.coreference_gold = []
        self.links = self.multi_sieve.links
        # TODO remove or implement self.local_mentions = self.local_mentions_constant in extractor_options
        self.wrong_purged = {}
        self.not_purged = {}
        self.ok_purged = {}
        self.all_purged = {}
        self.entities_purged = []

    def get_meta(self):
        """  Recover the statistics obtained while processing the graph.

        :return: A struck of dictionaries.
        """

        return {"sieves": self.multi_sieve.get_meta(),
                "extractor": self.candidate_extractor.get_meta(),
                "purges":  {
                    "ALL_PURGED": self.wrong_purged,
                    "WRONG_PURGED": self.wrong_purged,
                    "NOT_PURGED": self.not_purged,
                    "OK_PURGED": self.ok_purged}
                }

    def load_purges(self, mention_purges):
        """ Load the purges based on short-names list.

        :param mention_purges: List of short-names of purges.
        :return: a list of purge objects.
        """
        self.logger.info("Purges: %s", mention_purges)
        return [purges_by_name[purge_name](
                self.graph_builder, self)
                for purge_name in mention_purges]

    def process_sentence(self, sentence):
        """ Fetch the sentence mentions and generate candidates for they.

        :param sentence: The sentence syntactic tree root node.
        """
        # Extract the mentions
        mentions_candidate_order, mentions_text_order = \
            self.candidate_extractor.process_sentence(sentence=sentence)
        # Add new clusters and candidates
        # self.add_candidatures(mentions_bft, mentions_text_order)
        self.mentions_candidate_order.append(mentions_candidate_order)
        self.mentions_textual_order.append(mentions_text_order)

    def resolve_text(self):
        """ For a candidate marked graph, resolve the coreference.
        """

        # self.logger.info("Processing Coreference (%s candidates)", len(self.mentions))

        indexed_clusters = 0
        # Pass the sieves to resolve the coreference
        coreference_proposal = self.multi_sieve.process(
            graph_builder=self.graph_builder,
            mentions_text_order=self.mentions_textual_order,
            mentions_candidate_order=self.mentions_candidate_order)
        gold_mentions = [m[SPAN] for m in self.graph_builder.get_all_gold_mentions()]

        self.logger.info("POST-Processing Coreference (%s clusters)", len(coreference_proposal))
        # From the coreference cluster add the acceptable result to the graph
        for index, entity in enumerate(coreference_proposal):
            # Remove the singletons
            mentions = []
            for unfiltered_mention in entity:
                for purge in self.purges:
                    if purge.purge_mention(unfiltered_mention):
                        self.all_purged[unfiltered_mention[ID]] = \
                            [unfiltered_mention[FORM], unfiltered_mention[SPAN], purge.short_name]
                        self.logger.debug("purged mention(%s): %s",
                                          purge.short_name, unfiltered_mention[FORM])
                        if self.soft_purges:
                            coreference_proposal.append([unfiltered_mention, ])
                        if unfiltered_mention[SPAN] in gold_mentions:
                            self.logger.info("Wrong purged")
                            self.wrong_purged[unfiltered_mention[ID]] =\
                                [unfiltered_mention[FORM], unfiltered_mention[SPAN], purge.short_name]
                        else:
                            self.ok_purged[unfiltered_mention[ID]] = \
                                [unfiltered_mention[FORM], unfiltered_mention[SPAN], purge.short_name]
                        break
                else:
                    if unfiltered_mention[SPAN] not in gold_mentions:
                        self.logger.info("Not purged purged")
                        self.not_purged[unfiltered_mention[ID]] = \
                            [unfiltered_mention[FORM], unfiltered_mention[SPAN]]
                    mentions.append(unfiltered_mention)
            if len(mentions) == 0:
                continue

            for purge in self.purges:
                if purge.purge_entity(mentions):
                    self.entities_purged.append((",".join((mention[ID] for mention in mentions)), purge.short_name))
                    self.logger.debug("Purged entity: %s", purge.short_name)
                    break
            else:
                # Add the entity
                self.graph_builder.add_coref_entity(
                    entity_id="EN{0}".format(index), mentions=mentions)
                indexed_clusters += 1
        self.logger.info("Indexed clusters: %d", indexed_clusters)
