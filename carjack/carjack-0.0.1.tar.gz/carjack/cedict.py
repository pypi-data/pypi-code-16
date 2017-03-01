# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import
import io
import os
import re
import sys
from zipfile import ZipFile

import requests

from carjack.util import ChineseWord

class CEDict(dict):
    def __init__(self, dictfile=None):
        self.url = 'https://www.mdbg.net/chindict/export/cedict/cedict_1_0_ts_utf-8_mdbg.zip'
        self.zipfilename = self.url.rpartition('/')[2]
        self.filename = 'cedict_ts.u8'
        if dictfile:
            self.load(dictfile)
        else:
            self.fetch()
            self.load(self.filename)

    def fetch(self):
        print ('Downloading from {} ...'.format(self.url), file=sys.stderr)
        r = requests.get(self.url, stream=True)
        print ('Extracting {} ...'.format(self.zipfilename), file=sys.stderr)
        with ZipFile(io.BytesIO(r.content), 'r') as zipfin:
            zipfin.extractall()
        print ('Extracted {} to {}'.format(self.filename, os.getcwd()))

    def load(self, dictfile):
        print ('Loading {} ...'.format(self.filename))
        with io.open(dictfile, 'r', encoding='utf8') as fin:
            for line in fin:
                if line.startswith('#'):
                    continue
                # Magic regex, see http://stackoverflow.com/q/41844240/610569
                s = re.search(r'^(\S+)\s+(\S+)\s+\[([^]]+)\]\s+\/(.*)\/$', line)
                trad, sim, pinyin = s.group(1), s.group(2), s.group(3)
                glosses = s.group(4).split('/')
                self[sim] = ChineseWord(traditional=trad, simplified=sim,
                                          pinyin=pinyin, glosses=glosses)

    def simplified_words(self):
        return self.keys()

    def traditional_words(self):
        return [w.traditional for w in self.values()]

    def glosses(self, word):
        return self[word].glosses

    def pinyin(self, word):
        return self[word].pinyin
