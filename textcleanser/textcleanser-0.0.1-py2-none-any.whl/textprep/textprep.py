#-*-coding:utf-8-*-
__author__ = 'cchen'


import types
from dialect import Dialect, twitter
from utils import *


class Cleanser(object):

    def __init__(self, dialect='twitter', **kwargs):
        """
        Args:
            dialect (str, object):
            **kwargs ():
        """
        if isinstance(dialect, str):
            exec 'self.dialect = %s(**kwargs)' % (dialect)
        elif isinstance(dialect, object):
            self.dialect = dialect(**kwargs)

    def cleanse(self, text):
        """
        Args:
            text (str):
        """

        if self.dialect.to_lower:
            text = text.lower()
        if self.dialect.remove_repeated_char:
            text = remove_repeated_char(text)
        if self.dialect.remove_newlines:
            text = remove_newlines(text)
        if self.dialect.remove_illformed:
            text = remove_illformed(text, self._lexicon_illformed)
        return text

    @staticmethod
    def load_illformed_lexicon():
        # Dataset: http://people.eng.unimelb.edu.au/tbaldwin/etc/lexnorm_v1.2.tgz
        with open('lexicon/corpus.v1.2.tweet', 'r') as i:
            csvreader = csv.reader(i, delimiter='\t')
            lexicon = dict()
            for row in csvreader:
                print row
                if len(row) == 3 and row[1] == 'OOV' and len(row[2]) > len(lexicon.get(row[0], '')):
                    lexicon[row[0]] = row[2]
        return lexicon

    @property
    def dialect(self):
        return self._dialect

    @dialect.setter
    def dialect(self, value):
        if isinstance(value, types.ClassType):
            raise TypeError("'%s' is not inherited from Dialect class" % str(value))
        self._dialect = value
        if self._dialect.remove_illformed:
            self.lexicon_illformed = self.load_illformed_lexicon()

    @property
    def lexicon_illformed(self):
        return self._lexicon_illformed

    @lexicon_illformed.setter
    def lexicon_illformed(self, value):
        self._lexicon_illformed = value
        self._dialect.remove_illformed = True

