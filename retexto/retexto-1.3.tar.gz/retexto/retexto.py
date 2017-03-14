# -*- coding: UTF-8 -*-
import re
import unicodedata
import string
import sys
from .unicodes_codes import *
from .stopwords import *


PY2 = int(sys.version[0]) == 2

if PY2:
    from unidecode import unidecode
    TEXT_TYPE = unicode
    BINARY_TYPE = str
    STR_TYPES = (str, unicode)
    IS_CHAR = list(unicode(string.ascii_letters, 'utf-8'))
else:
    TEXT_TYPE = str
    BINARY_TYPE = bytes
    unicode = str
    STR_TYPES = (str, )
    IS_CHAR = list(string.ascii_letters)
    basestring = (str, bytes)
    unidecode = str

MAP_CHARS = dict()
MAP_CHARS.update({ord(' '): ' '})
for c in IS_CHAR:
    MAP_CHARS.update({ord(unicode(c)): c})
ENCODE = 'utf-8'
STR_PUNC = list(string.punctuation)
REGEX_HTML = re.compile(r'<[^>]*>')
REGEX_MENTIONS = re.compile(r'\S*[@](?:\[[^\]]+\]|\S+)')
REGEX_TAGS = re.compile(r'\S*[#](?:\[[^\]]+\]|\S+)')
REGEX_SMILES = re.compile(r'([j|h][aeiou]){3,}')
REGEX_VOWELS = re.compile(r'([aeiou])\1+')
REGEX_CONSONANTS = re.compile(r'([b-df-hj-np-tv-z])\1+')
REGEX_SPACES = re.compile(r' +')
REGEX_URLS = re.compile(r'(www|http|https)(?:[a-zA-Z]|[0-9]|[$-_@.&+]|\
[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
MAP_TILDE = [
    ord(u'Á'), ord(u'É'), ord(u'Í'),
    ord(u'Ó'), ord(u'Ú'), ord(u'Ñ'),
    ord(u'À'), ord(u'È'), ord(u'Ì'),
    ord(u'Ò'), ord(u'Ù'), ord(u'ç'),
    ord(u'á'), ord(u'é'), ord(u'í'),
    ord(u'ó'), ord(u'ú'), ord(u'ñ'),
    ord(u'à'), ord(u'è'), ord(u'ì'),
    ord(u'ò'), ord(u'ù'), ord(u'ü'),
    ord(u'ä'), ord(u'ë'), ord(u'ï'),
    ord(u'ö'), ord(u'ü'), ord(u'ÿ'),
    ord(u'Ç')
]
REGEX_EMOJIS = re.compile(u'[\U0001F600-\U0001F64F]', re.UNICODE)


# print unidecode(u'😂'.decode(ENCODE))
class ReTexto:
    @classmethod
    def __init__(self, text):
        self.TEXT = text.rstrip()

    @classmethod
    def __repr__(self):
        return self.TEXT

    @staticmethod
    def is_unicode(v, encoding='utf-8'):
        if isinstance(encoding, basestring):
            encoding = ((encoding,),) + \
                        (('windows-1252',), (ENCODE, 'ignore'))
        if isinstance(v, BINARY_TYPE):
            for e in encoding:
                try:
                    return v.decode(*e)
                except:
                    pass
            return v
        return unicode(v)

    @classmethod
    def remove_html(self, by=''):
        try:
            return ReTexto(re.sub(REGEX_HTML, by, self.TEXT))
        except Exception as e:
            print(e)

    @classmethod
    def remove_mentions(self, by=''):
        try:
            return ReTexto(re.sub(
                                REGEX_MENTIONS,
                                by, self.is_unicode(self.TEXT)))
        except Exception as e:
            print(e)

    @classmethod
    def remove_tags(self, by=''):
        try:
            return ReTexto(re.sub(REGEX_TAGS, by, self.TEXT))
        except Exception as e:
            print(e)

    @classmethod
    def remove_smiles(self, by=''):
        try:
            return ReTexto(re.sub(REGEX_SMILES, by, self.TEXT))
        except Exception as e:
            print(e)

    @classmethod
    def remove_punctuation(self, by=''):
        l_text = []
        l_unicodes = set(UNICODE_EMOJI.keys())
        for char in list(self.TEXT):
            if not (char in STR_PUNC):
                l_text.append(char)
                continue
            l_text.append(by)
        return ReTexto(''.join(l_text))

    @classmethod
    def remove_nochars(self, preserve_tilde=False):
        chars = MAP_CHARS.keys()
        if preserve_tilde:
            chars += MAP_TILDE
        l_char = set(chars)
        l_text = []
        for char in list(self.is_unicode(self.TEXT)):
            if ord(char) in l_char:
                l_text.append(char)
                continue
        return ReTexto(''.join(l_text))

    @classmethod
    def remove_stopwords(self, lang=None):
        l_text = []
        sw = stopwords(lang)
        for char in self.split_words():
            if not (self.is_unicode(char) in sw):
                l_text.append(char)
        return ReTexto(' '.join(l_text))

    @classmethod
    def convert_specials(self):
        return ReTexto(unidecode(self.is_unicode(self.TEXT)))

    @classmethod
    def convert_emoji(self):
        text = self.TEXT
        if PY2:
            if not isinstance(self.TEXT, unicode):
                text = self.TEXT.decode('utf-8')
            r = re.sub(REGEX_EMOJIS, lambda m: emoji_name(m), text)
            r = r.encode(ENCODE)
        else:
            r = re.sub(REGEX_EMOJIS, lambda m: emoji_name(m), text)
        return ReTexto(r)

    @classmethod
    def remove_url(self, by=''):
        return ReTexto(re.sub(REGEX_URLS, '', self.TEXT))

    @classmethod
    def remove_duplicate_consonants(self):
        return ReTexto(re.sub(REGEX_CONSONANTS, r'\1', self.TEXT))

    @classmethod
    def remove_duplicate(self, r='a-z'):
        p = re.compile(r'([%s])\1+' % r)
        return ReTexto(re.sub(p, r'\1', self.TEXT))

    @classmethod
    def remove_duplicate_vowels(self):
        return ReTexto(re.sub(REGEX_VOWELS, r'\1', self.TEXT))

    @classmethod
    def remove_multispaces(self):
        return ReTexto(re.sub(REGEX_SPACES, ' ', self.TEXT))

    @classmethod
    def split_words(self, uniques=False):
        l = self.TEXT.split()
        if uniques:
            seen = set()
            l = [x for x in l if x not in seen and not seen.add(x)]
        return l

    @classmethod
    def lower(self):
        return ReTexto(self.TEXT.lower())
