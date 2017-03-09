# coding: utf-8

import unicodedata

from Products.CMFPlone.UnicodeSplitter.config import (
    rx_U,
    rxGlob_U,
    rx_L,
    rxGlob_L,
    rx_all,
    pattern,
    pattern_g
    )


def bigram(u, limit=1):
    """Split into bi-gram.
    limit arg describes ending process.
    If limit = 0 then
        日本人-> [日本,本人, 人]
        金 -> [金]
    If limit = 1 then
        日本人-> [日本,本人]
        金 -> [金]
    """
    # print(u)
    if len(u) == 1:
        return [u]
    else:
        return [u[i:i + 2] for i in xrange(len(u) - limit)]


def process_unicode(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.
    """
    # print(uni)
    normalized = unicodedata.normalize('NFKC', uni)
    for word in rx_U.findall(normalized):
        swords = [g.group() for g in pattern.finditer(word)]
        for sword in swords:
            if not rx_all.match(sword[0]):
                yield sword
            else:
                for x in bigram(sword, 1): #TODO
                    yield x

def process_unicode_glob(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.  Considering globbing.
    """
    # print(uni)
    # import pdb;pdb.set_trace()
    normalized = unicodedata.normalize('NFKC', uni)
    for word in rxGlob_U.findall(normalized):
        swords = [g.group() for g in pattern_g.finditer(word)
                  if g.group() not in u"*?"]
        for i, sword in enumerate(swords):
            if not rx_all.match(sword[0]):
                yield sword
            else:
                # if i == len(swords) - 1:
                #     limit = 1
                # else:
                #     limit = 0
                limit = 1 #TODO
                if len(sword) == 1:
                    bigramed = [sword + u"*"]
                    # bigramed = [sword] #TODO
                else:
                    bigramed = bigram(sword, limit)
                for x in bigramed:
                    yield x
