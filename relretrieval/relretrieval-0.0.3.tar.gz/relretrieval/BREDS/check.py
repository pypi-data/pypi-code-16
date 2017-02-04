#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cPickle
import sys
import os
import codecs
import operator
import re

from numpy import dot
from gensim import matutils
from collections import defaultdict
from nltk.data import load
from nltk.corpus import stopwords
from nltk import WordNetLemmatizer
from gensim.models import Word2Vec

from Seed import Seed
from Pattern import Pattern
# from Config import Config
from Tuple import Tuple
# from Sentence import Sentence
from ReVerb import Reverb

from relretrieval.es.relretrieval_manager import SentenceManager, PatternManager


# useful for debugging
PRINT_TUPLES = True
PRINT_PATTERNS = True


class MyConfig():

    def __init__(self, similarity, confidence):
        # http://www.ling.upenn.edu/courses/Fall_2007/ling001/penn_treebank_pos.html
        # select everything except stopwords, ADJ and ADV
        self.filter_pos = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS', 'WRB']
        self.regex_clean_simple = re.compile('</?[A-Z]+>', re.U)
        self.regex_clean_linked = re.compile('</[A-Z]+>|<[A-Z]+ url=[^>]+>', re.U)
        self.tags_regex = re.compile('</?[A-Z]+>', re.U)
        self.e_types = {'ORG': 3, 'LOC': 4, 'PER': 5}
        self.positive_seed_tuples = set()
        self.negative_seed_tuples = set()
        self.vec_dim = 0
        self.e1_type = None
        self.e2_type = None
        self.stopwords = stopwords.words('english')
        self.lmtzr = WordNetLemmatizer()
        self.reverb = Reverb()
        self.threshold_similarity = similarity
        self.instance_confidence = confidence
        self.word2vec = None
        self.vec_dim = None

        # self.tag_type = "simple" or "linked"

        # simple tags, e.g.:
        # <PER>Bill Gates</PER>
        self.regex_simple = re.compile('<[A-Z]+>[^<]+</[A-Z]+>', re.U)

        # linked tags e.g.:
        # <PER url=http://en.wikipedia.org/wiki/Mark_Zuckerberg>Zuckerberg</PER>
        self.regex_linked = re.compile('<[A-Z]+ url=[^>]+>[^<]+</[A-Z]+>', re.U)

        self.max_tokens_away = 6           # maximum number of tokens between the two entities
        self.min_tokens_away = 1           # maximum number of tokens between the two entities
        self.context_window_size = 2       # number of tokens to the left and right

        self.wUpdt = 0.5                   # < 0.5 trusts new examples less on each iteration
        self.number_iterations = 4         # number of bootstrap iterations
        self.wUnk = 0.1                    # weight given to unknown extracted relationship instances
        self.wNeg = 2                      # weight given to extracted relationship instances
        self.min_pattern_support = 0  # 2       # minimum number of instances in a cluster to be considered a pattern

        self.word2vecmodelpath = "vectors.bin"   # path to a word2vecmodel in binary format

        self.alpha = 0.2                   # weight of the BEF context in the similarity function
        self.beta = 0.6                    # weight of the BET context in the similarity function
        self.gamma = 0.2                   # weight of the AFT context in the similarity function

        assert self.alpha + self.beta + self.gamma == 1

        self.e1_type = "LOCATION"  # "ORG"
        self.e2_type = "LOCATION"  # "LOC"

        self.positive_seed_tuples.add(Seed("Citibank", "Athens"))
        self.positive_seed_tuples.add(Seed("Nokia", "Espoo"))
        self.positive_seed_tuples.add(Seed("Motorola", "Schaumburg"))
        self.positive_seed_tuples.add(Seed("Pfizer", "New York"))
        self.positive_seed_tuples.add(Seed("Microsoft", "Redmond"))
        self.positive_seed_tuples.add(Seed("Berlin", "Germany"))

        self.negative_seed_tuples.add(Seed("Daiwa Bank Holdings Inc.", "Osaka"))
        self.negative_seed_tuples.add(Seed("Adelphia", "Coudersport"))

        print "Configuration parameters"
        print "========================\n"

        print "Relationship/Sentence Representation"
        print "e1 type              :", self.e1_type
        print "e2 type              :", self.e2_type
        # print "tags type            :", self.tag_type
        print "context window       :", self.context_window_size
        print "max tokens away      :", self.max_tokens_away
        print "min tokens away      :", self.min_tokens_away
        print "Word2Vec Model       :", self.word2vecmodelpath

        print "\nContext Weighting"
        print "alpha                :", self.alpha
        print "beta                 :", self.beta
        print "gamma                :", self.gamma

        print "\nSeeds"
        print "positive seeds       :", len(self.positive_seed_tuples)
        print "negative seeds       :", len(self.negative_seed_tuples)
        print "negative seeds wNeg  :", self.wNeg
        print "unknown seeds wUnk   :", self.wUnk

        print "\nParameters and Thresholds"
        print "threshold_similarity :", self.threshold_similarity
        print "instance confidence  :", self.instance_confidence
        print "min_pattern_support  :", self.min_pattern_support
        print "iterations           :", self.number_iterations
        print "iteration wUpdt      :", self.wUpdt
        print "\n"

        self.word2vec = {}

    def read_word2vec(self):
        print "Loading word2vec model ...\n"
        self.word2vec = Word2Vec.load_word2vec_format(
            self.word2vecmodelpath, binary=True
        )
        self.vec_dim = self.word2vec.layer1_size
        print self.vec_dim, "dimensions"


class Relationship:

    def __init__(self, sentence_id, _before, _between, _after, _ent1, _ent2,
                 e1_type, e2_type):
        self.sentence_id = sentence_id
        self.before = _before
        self.between = _between
        self.after = _after
        self.e1 = _ent1
        self.e2 = _ent2
        self.e1_type = e1_type
        self.e2_type = e2_type

    def __eq__(self, other):
        if self.e1 == other.e1 and self.before == other.before and \
            self.between == other.between \
                and self.after == other.after:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.e1) ^ hash(self.e2) ^ hash(self.before) ^ \
            hash(self.between) ^ hash(self.after)


class BREDS(object):

    def __init__(self, similarity, confidence):
        self.curr_iteration = 0
        self.patterns = list()
        self.processed_tuples = list()
        self.candidate_tuples = defaultdict(list)
        self.config = MyConfig(similarity, confidence)

    def generate_tuples(self, es_host=""):
        """
        Generate tuples instances from a text file with sentences where
        named entities are already tagged
        """

        # ひとまずコメントアウト
        # self.config.read_word2vec()

        # tagger = load('taggers/maxent_treebank_pos_tagger/english.pickle')
        print "\nGenerating relationship instances from sentences"

        sentence_manager = SentenceManager(host=os.getenv("ELASTICSEARCH_URL"))
        sentences = sentence_manager.get_sentences_having_more_than_two_entities()
        print "sentences", sentences
        # return

        count = 0
        for sentence in sentences:
            count += 1
            if count % 10000 == 0:
                sys.stdout.write(".")

            relationships = self.extract_relationships(sentence, self.config)

            for rel in relationships:
                t = Tuple(rel.e1, rel.e2, rel.sentence_id, rel.before,
                          rel.between, rel.after, self.config)
                self.processed_tuples.append(t)

        print "\n", len(self.processed_tuples), "tuples generated"
        # print "Writing generated tuples to disk"
        # f = open("processed_tuples.pkl", "wb")
        # cPickle.dump(self.processed_tuples, f)
        # f.close()

    def extract_relationships(self, sentence, config):
        relationships = list()
        tokens = [token["token"] for token in sentence["tokens"]]
        print tokens
        entities = sentence["entities"]
        window_size = config.context_window_size
        n = len(entities)
        for i in xrange(n - 1):
            for j in xrange(i + 1, n):
                # print i, j
                e1_index = entities[i]["token_index"]
                e2_index = entities[j]["token_index"]
                d = e2_index - e1_index - 1
                e1_label = entities[i]["label"]
                e2_label = entities[j]["label"]
                if config.max_tokens_away >= d >= config.min_tokens_away \
                    and e1_label == config.e2_type \
                        and e2_label == config.e2_type:
                    before = tokens[e1_index - window_size:e1_index]
                    between = tokens[e1_index + 1:e2_index]
                    after = tokens[e2_index + 1:e2_index + window_size + 1]

                    print before
                    print between
                    print after

                    r = Relationship(
                        sentence["id"],
                        before, between, after,
                        entities[i]["token"], entities[j]["token"],
                        e1_label, e2_label)
                    relationships.append(r)
                else:
                    print "not match", i, j

        return relationships

    def similarity_3_contexts(self, p, t):
        (bef, bet, aft) = (0, 0, 0)

        if t.bef_vector is not None and p.bef_vector is not None:
            bef = dot(
                matutils.unitvec(t.bef_vector), matutils.unitvec(p.bef_vector)
            )

        if t.bet_vector is not None and p.bet_vector is not None:
            bet = dot(
                matutils.unitvec(t.bet_vector), matutils.unitvec(p.bet_vector)
            )

        if t.aft_vector is not None and p.aft_vector is not None:
            aft = dot(
                matutils.unitvec(t.aft_vector), matutils.unitvec(p.aft_vector)
            )

        return self.config.alpha * bef + self.config.beta * bet + self.config.gamma * aft

    def similarity_all(self, t, extraction_pattern):

        # calculates the cosine similarity between all patterns part of a
        # cluster (i.e., extraction pattern) and the vector of a ReVerb pattern
        # extracted from a sentence;

        # returns the max similarity scores

        good = 0
        bad = 0
        max_similarity = 0

        for p in list(extraction_pattern.tuples):
            score = self.similarity_3_contexts(t, p)
            if score > max_similarity:
                max_similarity = score
            if score >= self.config.threshold_similarity:
                good += 1
            else:
                bad += 1

        if good >= bad:
            return True, max_similarity
        else:
            return False, 0.0

    def match_seeds_tuples(self):

        # checks if an extracted tuple matches seeds tuples

        matched_tuples = list()
        count_matches = dict()
        for t in self.processed_tuples:
            for s in self.config.positive_seed_tuples:
                if t.e1 == s.e1 and t.e2 == s.e2:
                    matched_tuples.append(t)
                    try:
                        count_matches[(t.e1, t.e2)] += 1
                    except KeyError:
                        count_matches[(t.e1, t.e2)] = 1

        return count_matches, matched_tuples

    def write_relationships_to_disk(self):
        print "\nWriting extracted relationships to disk"
        print "self.candidate_tuples", self.candidate_tuples
        f_output = open("relationships.txt", "w")
        tmp = sorted(self.candidate_tuples.keys(), reverse=True)
        try:
            for t in tmp:
                f_output.write(
                    "instance: " + t.e1.encode("utf8") + '\t' +
                    t.e2.encode("utf8") + '\tscore:' + str(t.confidence) +
                    '\n')
                f_output.write("sentence_id: " + t.sentence_id.encode("utf8") + '\n')
                f_output.write("pattern_bef: " +
                               " ".join([w.encode("utf8") for w in t.bef_words]) + '\n')
                f_output.write("pattern_bet: " +
                               " ".join([w.encode("utf8") for w in t.bet_words]) + '\n')
                f_output.write("pattern_aft: " +
                               " ".join([w.encode("utf8") for w in t.aft_words]) + '\n')
                if t.passive_voice is False:
                    f_output.write("passive voice: False\n")
                elif t.passive_voice is True:
                    f_output.write("passive voice: True\n")
                f_output.write("\n")
            f_output.close()
        except Exception, e:
            print e
            sys.exit(1)

    def init_bootstrap(self, tuples):

        # starts a bootstrap iteration

        # if tuples is not None:
        #     f = open(tuples, "r")
        #     print "\nLoading processed tuples from disk..."
        #     self.processed_tuples = cPickle.load(f)
        #     f.close()
        #     print len(self.processed_tuples), "tuples loaded"

        self.curr_iteration = 0
        while self.curr_iteration <= self.config.number_iterations:
            print "=========================================="
            print "\nStarting iteration", self.curr_iteration
            print "\nLooking for seed matches of:"
            for s in self.config.positive_seed_tuples:
                print s.e1, '\t', s.e2

            # Looks for sentences matching the seed instances
            count_matches, matched_tuples = self.match_seeds_tuples()

            print "count_matches", count_matches
            print "matched_tuples", matched_tuples

            # return

            if len(matched_tuples) == 0:
                print "\nNo seed matches found"
                sys.exit(0)

            else:
                print "\nNumber of seed matches found"
                sorted_counts = sorted(
                    count_matches.items(),
                    key=operator.itemgetter(1),
                    reverse=True
                )
                for t in sorted_counts:
                    print t[0][0], '\t', t[0][1], t[1]

                print "\n", len(matched_tuples), "tuples matched"

                # Cluster the matched instances, to generate
                # patterns/update patterns
                print "\nClustering matched instances to generate patterns"
                self.cluster_tuples(matched_tuples)
                print "self.patterns", self.patterns

                # print self.patterns[0].tuples[0]

                # Eliminate patterns supported by less than
                # 'min_pattern_support' tuples
                new_patterns = [p for p in self.patterns if len(p.tuples) >
                                self.config.min_pattern_support]
                self.patterns = new_patterns

                print "\n", len(self.patterns), "patterns generated"

                if PRINT_PATTERNS is True:
                    count = 1
                    print "\nPatterns:"
                    for p in self.patterns:
                        print count
                        for t in p.tuples:
                            print "BEF", t.bef_words
                            print "BET", t.bet_words
                            print "AFT", t.aft_words
                            print "========"
                            print "\n"
                        count += 1

                if self.curr_iteration == 0 and len(self.patterns) == 0:
                    print "No patterns generated"
                    sys.exit(0)

                # Look for sentences with occurrence of seeds
                # semantic types (e.g., ORG - LOC)
                # This was already collect and its stored in:
                # self.processed_tuples
                #
                # Measure the similarity of each occurrence with each
                # extraction pattern and store each pattern that has a
                # similarity higher than a given threshold
                #
                # Each candidate tuple will then have a number of patterns
                # that extracted it each with an associated degree of match.
                print "Number of tuples to be analyzed:", \
                    len(self.processed_tuples)

                print "\nCollecting instances based on extraction patterns"
                count = 0

                for t in self.processed_tuples:

                    count += 1
                    if count % 1000 == 0:
                        sys.stdout.write(".")
                        sys.stdout.flush()

                    sim_best = 0
                    pattern_best = None
                    print "self.patterns", self.patterns
                    for extraction_pattern in self.patterns:
                        accept, score = self.similarity_all(
                            t, extraction_pattern
                        )
                        print "accept", accept, "score", score
                        if not pattern_best:
                            score = 0.1
                        if accept is True:
                            extraction_pattern.update_selectivity(
                                t, self.config
                            )
                            if score > sim_best:
                                sim_best = score
                                pattern_best = extraction_pattern

                    if sim_best >= self.config.threshold_similarity:
                        # if this tuple was already extracted, check if this
                        # extraction pattern is already associated with it,
                        # if not, associate this pattern with it and store the
                        # similarity score
                        patterns = self.candidate_tuples[t]
                        if patterns is not None:
                            if pattern_best not in [x[0] for x in patterns]:
                                self.candidate_tuples[t].append(
                                    (pattern_best, sim_best)
                                )

                        # If this tuple was not extracted before
                        # associate this pattern with the instance
                        # and the similarity score
                        else:
                            self.candidate_tuples[t].append(
                                (pattern_best, sim_best)
                            )

                # update all patterns confidence
                for p in self.patterns:
                    p.update_confidence(self.config)

                if PRINT_PATTERNS is True:
                    print "\nPatterns:"
                    for p in self.patterns:
                        for t in p.tuples:
                            print "BEF", t.bef_words
                            print "BET", t.bet_words
                            print "AFT", t.aft_words
                            print "========"
                        print "Positive", p.positive
                        print "Negative", p.negative
                        print "Unknown", p.unknown
                        print "Tuples", len(p.tuples)
                        print "Pattern Confidence", p.confidence
                        print "\n"

                # update tuple confidence based on patterns confidence
                print "\n\nCalculating tuples confidence"
                for t in self.candidate_tuples.keys():
                    confidence = 1
                    t.confidence_old = t.confidence
                    for p in self.candidate_tuples.get(t):
                        print "p", p
                        confidence *= 1 - (p[0].confidence * p[1])
                    t.confidence = 1 - confidence

                # sort tuples by confidence and print
                if PRINT_TUPLES is True:
                    extracted_tuples = self.candidate_tuples.keys()
                    tuples_sorted = sorted(
                        extracted_tuples,
                        key=lambda tpl: tpl.confidence,
                        reverse=True
                    )
                    for t in tuples_sorted:
                        print t.sentence_id
                        print t.e1, t.e2
                        print t.confidence
                        print "\n"

                print "Adding tuples to seed with confidence >=" + \
                      str(self.config.instance_confidence)
                for t in self.candidate_tuples.keys():
                    if t.confidence >= self.config.instance_confidence:
                        seed = Seed(t.e1, t.e2)
                        self.config.positive_seed_tuples.add(seed)

                # increment the number of iterations
                self.curr_iteration += 1

        self.write_relationships_to_disk()
        self.save_patters()

    def cluster_tuples(self, matched_tuples):
        # this is a single-pass clustering
        # Initialize: if no patterns exist, first tuple goes to first cluster
        if len(self.patterns) == 0:
            c1 = Pattern(matched_tuples[0])
            self.patterns.append(c1)

        count = 0
        for t in matched_tuples:
            count += 1
            if count % 1000 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            max_similarity = 0
            max_similarity_cluster_index = 0

            # go through all patterns(clusters of tuples) and find the one
            # with the highest similarity score
            for i in range(0, len(self.patterns), 1):
                extraction_pattern = self.patterns[i]
                accept, score = self.similarity_all(t, extraction_pattern)
                print "accept", accept, "score", score
                if accept is True and score > max_similarity:
                    max_similarity = score
                    max_similarity_cluster_index = i

            # if max_similarity < min_degree_match create a new cluster having
            #  this tuple as the centroid
            if max_similarity < self.config.threshold_similarity:
                c = Pattern(t)
                self.patterns.append(c)

            # if max_similarity >= min_degree_match add to the cluster with
            # the highest similarity
            else:
                self.patterns[max_similarity_cluster_index].add_tuple(t)

    def save_patters(self):
        print "save_patters"
        print self.patterns
        pattern_manager = PatternManager(os.getenv("ELASTICSEARCH_URL"))

        for p in self.patterns:
            relations = []
            for t in p.tuples:
                relation = {
                    "BEF": " ".join(t.bef_words),
                    "BET": " ".join(t.bet_words),
                    "AFT": " ".join(t.aft_words),
                    "tuples": [
                        {
                            "first": t.e1,
                            "second": t.e2,
                        },
                    ],
                }
                relations.append(relation)
            pattern_manager.save({"relations": relations})


def main():
    pattern_manager = PatternManager(host=os.getenv("ELASTICSEARCH_URL"))
    body = {
        "query": {"match_all": {}}
    }
    res = pattern_manager.search(body)

    print res

    return

    similarity = 0.0
    confidence = 0.0

    breads = BREDS(similarity, confidence)
    breads.generate_tuples()
    breads.init_bootstrap(tuples=None)

if __name__ == "__main__":
    main()
