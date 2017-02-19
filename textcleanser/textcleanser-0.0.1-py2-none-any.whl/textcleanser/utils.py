#-*-coding:utf-8-*-
__author__ = 'cchen'


import re
import csv


def remove_repeated_char(text):
    return re.sub(r'(.+)\1{2,}', r'\1\1', text)


def remove_newlines(text):
    text = re.sub('\n|\r', ' ', text)
    return re.sub(' +', ' ', text)

def remove_illformed(text, lexicon):
    """

    Args:
        text (str):
        lexicon (dict):



    References:
        Gouws, Stephan, et al. "Contextual bearing on linguistic variation in social media."
        Proceedings of the Workshop on Languages in Social Media. Association for Computational Linguistics, 2011.

        Bo Han and Timothy Baldwin (2011) Lexical normalisation of short text messages: Makn sens a #twitter.
        In Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics, Portland, USA.

        Yi Yang and Jacob Eisenstein (2013) A Log-Linear Model for Unsupervised Text Normalization.
        In Proceedings of Conference on Empirical Methods in Natural Language Processing (EMNLP), Seattle, USA
    """
    pattern = re.compile(r'\b(' + r'|'.join(lexicon.keys()) + r')\b')
    text = pattern.sub(lambda x: lexicon[x.group()], text)
    return text