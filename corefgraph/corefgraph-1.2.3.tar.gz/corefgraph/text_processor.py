# coding=utf-8
""" The entry module  of the corefgraph system . See process.file o process.corpus for CLI usage.

"""

import logging
from collections import Counter, defaultdict

from corefgraph.constants import SPAN, FORM, ID, NER
from corefgraph.graph.nafbuilder import NafAndTreeGraphBuilder
from corefgraph.multisieve import features
from corefgraph.multisieve.core import CoreferenceProcessor
from corefgraph.output import writers

__author__ = 'Josu Bermudez <josu.bermudez@deusto.es>'


class TextProcessor:
    """ Process a single text or corpus with several NLP stages managing the
    result as graphs.
    """

    def __init__(self, verbose, reader, secure_tree, lang, sieves,
                 extractor_options, mention_catchers,
                 mention_filters, mention_features, mention_purges):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        self.logger.info("Extractor Options %s", extractor_options)
        # Options
        self.lang = lang
        self.sieves = sieves
        self.extractor_options = extractor_options
        self.mention_catchers = mention_catchers
        self.mention_filters = mention_filters
        self.mention_purges = mention_purges

        # Graph builder and manager
        self.graph_builder = None
        self.coreference_processor = None
        self.feature_extractors = None
        self.meta = {}
        self.mention_features = mention_features
        self.reader = reader
        self.secure_tree = secure_tree

    def reset_graph(self):
        """Reset the graph and the elements that used a graph reference.

        """
        # Graph attributes
        self.graph_builder = NafAndTreeGraphBuilder(
            self.reader, self.secure_tree)
        self.coreference_processor = CoreferenceProcessor(
            graph_builder=self.graph_builder,
            extractor_options=self.extractor_options,
            sieves_list=self.sieves,
            mention_catchers=self.mention_catchers,
            mention_filters=self.mention_filters,
            mention_purges=self.mention_purges,
        )

        self.feature_extractors = [
            features.annotators_by_name[annotator](self.graph_builder)
            for annotator in self.mention_features]

        self.meta = defaultdict(Counter)

    def build_graph(self, document):
        """Build a graph form external parser.

        :param document: The document to generate the graph.
        """
        self.graph_builder.process_document(document=document)
        sentences_parsed = self.graph_builder.get_sentences()

        for index, sentence in enumerate(sentences_parsed):
            self.logger.debug("Loading Sentence %d", index)
            # syntax graph construction
            sentence_root = self.graph_builder.process_sentence(
                sentence=sentence,
                sentence_namespace="text@{0}".format(index),
                root_index=index)
            # Generate Coreference Candidatures for the sentence
            self.coreference_processor.process_sentence(sentence=sentence_root)

    def process_graph(self):
        """ Prepare the graph for output.
        """
        self.meta[self.graph_builder.doc_type] = self.graph_builder.get_doc_type()
        self.meta["sentences"] = []
        self.meta["features"] = defaultdict(Counter)
        # for sentence in self.coreference_processor.get_mentions():
        for index, sentence in enumerate(self.coreference_processor.mentions_textual_order):
            self.logger.debug("Featuring Sentence %d", index)
            sentence_mentions = []
            self.meta["sentences"].append(sentence_mentions)
            offset = len(sentence) and self.graph_builder.get_root(sentence[0])[SPAN][0]
            sentence_form = len(sentence) and self.graph_builder.get_root(sentence[0])[FORM]
            for mention in sentence:
                mention_meta = {
                    FORM: mention[FORM],
                    NER: mention.get(NER, '-None-'),
                    "sentence": sentence_form,
                    "headword": self.graph_builder.get_head_word(mention)[FORM],
                    SPAN: (mention[SPAN][0] - offset, mention[SPAN][1] - offset),
                    ID: mention[ID]}
                sentence_mentions.append(mention_meta)
                for feature_extractor in self.feature_extractors:
                    feature_extractor.extract_and_mark(mention=mention)
                    for feature in feature_extractor.features:
                        feature_value = mention.get(feature, "unset")
                        if isinstance(feature_value, dict):
                            feature_value = feature_value[ID]
                        if isinstance(feature_value, set)or isinstance(feature_value, list):
                            feature_value = list()
                            for f in feature_value:
                                if isinstance(f, dict):
                                    feature_value.append(f[ID])
                                else:
                                    feature_value.append(f)
                        else:
                            feature_value = feature_value
                        mention_meta[feature] = feature_value
                        try:
                            self.meta["features"][feature][feature_value] += 1
                        except TypeError:
                            self.meta["features"][feature]["NO_HASH"] += 1
        # Resolve the coreference
        self.logger.debug("Resolve Correference...")
        self.coreference_processor.resolve_text()

    def get_meta(self, ):
        self.meta.update(self.coreference_processor.get_meta())
        return self.meta

    def show_graph(self):
        """Show the graph in screen"""
        self.graph_builder.show_graph()

    def store(self, stream, config):
        """ Store the graph into a document with the format provided by the
        config.
        :param stream: The stream where the document is going to be write
        :param config: The config namespace that contains all the options needed
            for write the document.
        """
        kwargs = {}
        for option in config.writer_options:
            key, value = option.split()
            kwargs[key] = value

        writer = writers[config.writer](stream=stream, document_id=config.document_id)
        writer.store(
            graph_builder=self.graph_builder,
            encoding=config.encoding,
            language=config.language,
            coreference_processor=self.coreference_processor,
            start_time=config.start_time,
            end_time=config.end_time,
            **kwargs
        )

    def process_text(self, document):
        """ Generate a graph with all linguistic info from de document, resolve
        the coreference and output the results.

        :param document:
        """
        self.reset_graph()
        self.build_graph(document)
        self.process_graph()
