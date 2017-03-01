# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import io
import re
import sys
from itertools import chain
from collections import namedtuple, defaultdict

import requests
from bs4 import BeautifulSoup

from carjack.util import ChineseWord

class HSK(object):
    def __init__(self, hskfile=None):
        self.url = 'https://en.wiktionary.org/wiki/Appendix:HSK_list_of_Mandarin_words/'
        # Official level names.
        self.levels = ['Beginning_Mandarin', 'Elementary_Mandarin',
                       'Intermediate_Mandarin', 'Advanced_Mandarin']
        # Loads the hskfile.
        if hskfile:
            self.load(hskfile)
        else: # Else, fetch on wiktionary and save.
            self.fetch()
            self.save('hskfile.tsv')

        self.shortforms = {'beginner':self.beginning(), 'b':self.beginning(),
                           'beginning':self.beginning(),
                           'elementary':self.elementary(), 'e':self.elementary(),
                           'intermediate':self.intermediate(), 'i':self.intermediate(),
                           'advance':self.advance(), 'a':self.intermediate(),
                           'all':self.all()}

    def parse_wiktionary(self, soup):
        pattern = r'(.*?) \((?:(.*?), )?(.*?)\)'
        for tr in soup.find_all('tr'):
            for li in tr.find_all('li'):
                li = li.text.replace(u'\u200e', '')
                regex_search = re.search(pattern, li)
                if not regex_search:
                    continue
                sim, trad, pin = regex_search.groups()
                if any(ch in [u'／', u'/'] for ch in sim):
                    sim, *items  = reversed(re.split(u'／|/', sim))
                    trad = u'/'.join(items)
                yield ChineseWord(simplified=sim, traditional=trad, pinyin=pin,
                                  glosses=None)

    def fetch(self):
        self.word_lists = defaultdict(list)
        for level in self.levels:
            print ('Downloading {}...'.format(level), file=sys.stderr)
            url = self.url + level
            response = requests.get(url)
            content = response.content.decode('utf8')
            soup = BeautifulSoup(content, "html5lib")
            self.word_lists[level] = list(self.parse_wiktionary(soup))

    def save(self, filename):
        print ('Saving to {}'.format(filename), file=sys.stderr)
        with io.open(filename, 'w', encoding='utf8') as fout:
            for level in self.levels:
                for word in self.word_lists[level]:
                    print("\t".join([level, word.simplified,
                                     str(word.traditional), word.pinyin]),
                          end='\n', file=fout)

    def load(self, filename):
        self.word_lists = defaultdict(list)
        print ('Loaded {}'.format(filename), file=sys.stderr)
        with io.open(filename, 'r', encoding='utf8') as fin:
            for line in fin:
                level, sim, trad, pin = line.strip().split('\t')
                trad = None if trad == "None" else trad
                word = ChineseWord(simplified=sim, traditional=trad, pinyin=pin,
                                   glosses=None)
                self.word_lists[level].append(word)

    # Duck-type functions.
    def beginning(self):
        return self.word_lists['Beginning_Mandarin']
    def elementary(self):
        return self.word_lists['Elementary_Mandarin']
    def intermediate(self):
        return self.word_lists['Intermediate_Mandarin']
    def advance(self):
        return self.word_lists['Advanced_Mandarin']
    def all(self):
        return list(chain(*self.word_lists.values()))

    def words(self, level=None):
        if not level:
            level = 'all'
        return self.shortforms[level]
