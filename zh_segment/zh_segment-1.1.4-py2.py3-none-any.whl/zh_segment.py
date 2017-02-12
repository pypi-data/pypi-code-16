"""English Word Segmentation in Python

Word segmentation is the process of dividing a phrase without spaces back
into its constituent parts. For example, consider a phrase like "thisisatest".
For humans, it's relatively easy to parse. This module makes it easy for
machines too. Use `segment` to parse a phrase into its parts:

>>> from zh_segment import segment
>>> segment('1077501; 1296599; 5000; 5000; 4975; 36 months; 10.64%; 162.87; B; B2;;10+ years;RENT')
['1077501', '1296599', '5000', '5000', '4975', '36', 'months', '10.64%', '162.87', 'B', 'B2', '10+', 'years', 'RENT']

In the code, 1040034723697 is the total number of words in the corpus. A
subset of this corpus is found in unigrams.txt and bigrams.txt which
should accompany this file. A copy of these files may be found at
http://norvig.com/ngrams/ under the names count_1w.txt and count_2w.txt
respectively.

Copyright (c) 2016 by Z&H

Based on code from the chapter "Natural Language Corpus Data"
from the book "Beautiful Data" (Segaran and Hammerbacher, 2009)
http://oreilly.com/catalog/9780596157111/

Original Copyright (c) 2008-2009 by Peter Norvig

"""

import io
import math
import os.path as op
import sys
import re

ALPHABET = set('abcdefghijklmnopqrstuvwxyz0123456789')
SEPARATORS = set(';')
BIGRAMS = None
DATADIR = op.join(op.dirname(op.realpath(__file__)), 'zh_segment_data')
TOTAL = 1024908267229.0
UNIGRAMS = None


def clean(text):
    "Return `text` lower-cased with non-alphanumeric characters removed."
    return ''.join(letter.strip() for letter in text if letter not in SEPARATORS)


def divide(text, limit=24):
    """Yield `(prefix, suffix)` pairs from `text` with `len(prefix)` not
    exceeding `limit`.

    """
    for pos in range(1, min(len(text), limit) + 1):
        yield (text[:pos], text[pos:])


def load():
    "Load unigram and bigram counts from disk."
    global UNIGRAMS, BIGRAMS  # pylint: disable=global-statement
    UNIGRAMS = parse_file(op.join(DATADIR, 'unigrams.txt'))
    BIGRAMS = parse_file(op.join(DATADIR, 'bigrams.txt'))


def parse_file(filename):
    "Read `filename` and parse tab-separated file of (word, count) pairs."
    with io.open(filename, encoding='utf-8') as reader:
        lines = (line.split('\t') for line in reader)
        return dict((word, float(number)) for word, number in lines)


def score(word, prev=None):
    "Score a `word` in the context of the previous word, `prev`."
    if UNIGRAMS is None and BIGRAMS is None:
        load()

    word = word.lower()

    if prev is None:
        if word in UNIGRAMS:

            # Probability of the given word.

            return UNIGRAMS[word] / TOTAL
        else:
            # Penalize words not found in the unigrams according
            # to their length, a crucial heuristic.

            return 10.0 / (TOTAL * 10 ** len(word))
    else:
        prev = prev.lower()

        bigram = '{0} {1}'.format(prev, word)

        if bigram in BIGRAMS and prev in UNIGRAMS:

            # Conditional probability of the word given the previous
            # word. The technical name is *stupid backoff* and it's
            # not a probability distribution but it works well in
            # practice.

            return BIGRAMS[bigram] / TOTAL / score(prev)
        else:
            # Fall back to using the unigram probability.

            return score(word)


def isegment(text):
    "Return iterator of words that is the best segmenation of `text`."

    memo = dict()

    def search(text, prev='<s>'):
        "Return max of candidates matching `text` given previous word, `prev`."
        if text == '':
            return 0.0, []

        def candidates():
            "Generator of (score, words) pairs for all divisions of text."
            for prefix, suffix in divide(text):
                prefix_score = math.log10(score(prefix, prev))

                pair = (suffix, prefix)
                if pair not in memo:
                    memo[pair] = search(suffix, prefix)
                suffix_score, suffix_words = memo[pair]

                yield (prefix_score + suffix_score, [prefix] + suffix_words)

        return max(candidates())

    # Avoid recursion limit issues by dividing text into chunks, segmenting
    # those chunks and combining the results together. Chunks may divide words
    # in the middle so prefix chunks with the last five words of the previous
    # result.

    clean_text = clean(text)
    size = 250
    prefix = ''

    for offset in range(0, len(clean_text), size):
        chunk = clean_text[offset:(offset + size)]
        _, chunk_words = search(prefix + chunk)
        prefix = ''.join(chunk_words[-5:])
        del chunk_words[-5:]
        for word in chunk_words:
            yield word

    _, prefix_words = search(prefix)

    for word in prefix_words:
        yield word


def segment(text):
    "Return a list of words that is the best segmenation of `text`."
    result = []
    for x in re.split(';', text):
        result.extend(list(isegment(x)))
    return result


def parse_dic_from_excel(excel_file_name):
    return dict(), dict()


def segment_phrase(text, probability_dic, rate):
    result = segment(text)
    phrases = []
    phrase = ''
    for i in range(len(result) - 1):
        pair = '{0} {1}'.format(result[i].lower(), result[i + 1].lower())
        # TODO cluster to generate the rate automatically
        if pair not in probability_dic.keys() or probability_dic[pair] < rate:
            phrase += ' ' + result[i]
            phrases.append(phrase)
            phrase = result[i + 1]
    if len(phrase) == 0:
        phrases.append(phrase)
    return phrases


def main(args=()):
    """Command-line entry-point. Parses `args` into in-file and out-file then
    reads lines from in-file, segments the lines, and writes the result to
    out-file. Input and output default to stdin and stdout respectively.

    """
    import argparse
    import os

    parser = argparse.ArgumentParser(description='English Word Segmentation')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)

    streams = parser.parse_args(args)

    for line in streams.infile:
        streams.outfile.write(' '.join(segment(line)))
        streams.outfile.write(os.linesep)

if __name__ == '__main__':
    main(sys.argv[1:])

__title__ = 'zh_segment'
__version__ = '1.1.4'
__build__ = 0x000800
__author__ = 'Z&H'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 Z&H'
