import csv
import os
import re
import warnings

import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

from CMUTweetTagger import runtagger_parse


class Centiment:
    PATH = os.path.dirname(__file__)

    PATTERN = r"""(?x)              # set flag to allow verbose regexps
              (?:[A-Z]\.)+          # abbreviations, e.g. U.S.A.
              |\d+(?:\.\d+)?%?      # numbers, incl. currency and percentages
              |\w+(?:[-']\w+)*      # words w/ optional internal hyphens/apostrophe
              |\.\.\.               # ellipsis
              |(?:[.,;"'?():-_`])   # special characters with meanings
            """

    POS_SWITCH = {'JJ': wordnet.ADJ,
                  'VB': wordnet.VERB,
                  'NN': wordnet.NOUN,
                  'RB': wordnet.ADV}
    PATTERN_AVNR = re.compile('|'.join(POS_SWITCH.keys()))
    PATTERN_CONJ = re.compile(',|but|because')
    STOP_WORDS = frozenset(stopwords.words('english'))

    def __init__(self):
        self._lexicon = dict()
        self._lexicon_intensifier = self.load_lexicon(os.path.join(self.PATH, 'lexicon/int_dictionary1.11.txt'))
        self.PATTERN_INTENSIFIER = re.compile('|'.join(self.reversed_by(self._lexicon_intensifier)))
        self._replace_contraction = self.load_replace(os.path.join(self.PATH, 'lexicon/contractions.replace'))
        self.PATTERN_CONTRACTION = re.compile(r'(' + '|'.join(
            [re.escape(key) for key in self.reversed_by(self._replace_contraction)]) + ')')
        self._list_negation = self.load_list(os.path.join(self.PATH, 'lexicon/negation.list'))
        self.PATTERN_NEGATION = re.compile('|'.join(reversed(self._list_negation)))
        self._replace_prefix = self.load_replace(os.path.join(self.PATH, 'lexicon/prefix.replace'))
        self.PATTERN_PREFIX = re.compile(r'(' + '|'.join(
            [re.escape(key) for key in self.reversed_by(self._replace_prefix)]) + ')')
        self._lexicon_emoticons = self.load_lexicon(os.path.join(self.PATH, 'lexicon/emoticons.lex'), 5)
        self._lexicon['e'] = self._lexicon_emoticons

        self._replace_list = [
            self._replace_contraction,
            self._replace_prefix,
        ]

        self._multiwords = dict(map(lambda word:
                                    (re.sub('_', ' ', word), word),
                                    (word for word in self._lexicon_intensifier.keys() if '_' in word)))
        self._multiwords.update(dict(map(lambda word:
                                         (re.sub('_', ' ', word), word),
                                         (word for word in self._list_negation if '_' in word))))

        self._nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self._nltk_stemmer = WordNetLemmatizer()
        self._pos_tagger = lambda x: nltk.pos_tag(nltk.regexp_tokenize(x, self.PATTERN))

    def parse(self, text):
        if isinstance(text, list):
            return [self.parse(item) for item in text]
        else:
            text = re.sub(
                r'(' + '|'.join(sorted(self._multiwords.keys(), key=len, reverse=True)) + r')',
                lambda x: self._multiwords[x.group()], text)  # replace multi-words intensifier '_' connected
            sentences = self._nltk_splitter.tokenize(text)  # split sentences
            # tokenized_sentences = [nltk.regexp_tokenize(sentence, self.PATTERN) for sentence in sentences]  # split tokens
            # pos_tags = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
            return [self.parse_sentence(sentence) for sentence in sentences]

    def parse_sentence(self, sentence):
        for replace in self._replace_list:
            pattern = re.compile(r'(' + '|'.join(
                [re.escape(key) for key in self.reversed_by(replace)]) + ')')
            sentence = pattern.sub(lambda x: replace[x.group()], sentence)
        # sentence = self.PATTERN_CONTRACTION.sub(lambda x: self._replace_contraction[x.group()], sentence)
        # sentence = self.PATTERN_PREFIX.sub(lambda x: self._replace_prefix[x.group()], sentence)
        # sentence = nltk.regexp_tokenize(sentence, self.PATTERN)
        # pos = nltk.pos_tag(sentence)
        pos = self._pos_tagger(sentence)
        # print pos
        return self.parse_sentence_tokens_with_pos_tags(pos)

    def parse_sentence_tokens_with_pos_tags(self, sentence_tokens, previous_token=None,
                                            intensified_by=1., negated=1, has_not=1,
                                            part_acum_score=0., part_token_counts=0,
                                            sentence_scores=None):
        # print previous_token, part_acum_score
        if not sentence_tokens:
            if sentence_scores:
                sentence_scores.append(self.get_avg_score(part_acum_score,part_token_counts,
                                                          intensified_by, negated, has_not))
                # return sentence_scores
                # return sum(sentence_scores)
                return sum(sentence_scores) / len(sentence_scores)
            else:
                # print part_acum_score, part_token_counts, intensified_by, negated, has_not
                return self.get_avg_score(part_acum_score, part_token_counts, intensified_by, negated, has_not)

        else:
            current_token = sentence_tokens[0]
            current_pos_tag = current_token[1]
            current_word = current_token[0]
            intensifier = self.PATTERN_INTENSIFIER.search(current_word.lower())

            if current_pos_tag in ['@', '#'] or current_word in self.STOP_WORDS:
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated, has_not,
                                                                part_acum_score, part_token_counts,
                                                                sentence_scores)

            elif self.PATTERN_CONJ.search(current_word.lower()):
                if part_acum_score and part_token_counts:
                    current_sentence_score = self.get_avg_score(part_acum_score, part_token_counts,
                                                                intensified_by, negated, has_not)
                else:
                    return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                    1., 1, 1, 0, 0, sentence_scores)

                if sentence_scores:
                    if current_sentence_score:
                        sentence_scores.append(current_sentence_score)
                    return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                    1., 1, 1, 0, 0, sentence_scores)
                else:
                    if current_sentence_score:
                        return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                        1., 1, 1, 0, 0,
                                                                        [current_sentence_score])
                    else:
                        return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                        1., 1, 1, 0, 0,
                                                                        sentence_scores)

            elif current_word.lower() in self._lexicon_intensifier:
                intensified_by = 1. + self._lexicon_intensifier[intensifier.group()]
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated, has_not,
                                                                part_acum_score, part_token_counts,
                                                                sentence_scores)

            elif current_word.lower() == 'not':
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated, has_not * -1,
                                                                part_acum_score, part_token_counts,
                                                                sentence_scores)

            elif current_word.lower() in self._list_negation:
                # print current_token
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated * -1, has_not,
                                                                part_acum_score, part_token_counts,
                                                                sentence_scores)

            elif self.PATTERN_AVNR.search(current_pos_tag):
                # print current_word, current_pos_tag
                current_word, current_pos_tag = self.stem(current_word.lower(), current_pos_tag)
                # print current_word, current_pos_tag
                if current_word.startswith('anti-'):
                    current_word = current_word.split('-')[1]
                    current_score = self._lexicon['n'].get(current_word, 0.) * -1
                else:
                    current_score = self._lexicon[current_pos_tag].get(current_word, 0.)
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated, has_not,
                                                                part_acum_score + current_score, part_token_counts + 1,
                                                                sentence_scores)

            elif current_pos_tag in ['PRP', 'DT', '.']:
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated, has_not,
                                                                part_acum_score, part_token_counts,
                                                                sentence_scores)

            elif current_pos_tag == 'E':
                current_score = self._lexicon['emoji'].get(current_word.decode('utf-8'))
                current_score = self._lexicon['e'].get(current_word) if not current_score else current_score
                past_score = self.get_avg_score(part_acum_score,part_token_counts,
                                                intensified_by, negated, has_not)
                if past_score is not None:
                    if sentence_scores:
                        sentence_scores.append(past_score)
                    else:
                        sentence_scores = [past_score]
                if previous_token and current_score is not None:
                    sentence_scores.append(current_score)

                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by=1., negated=1, has_not=1,
                                                                part_acum_score=0., part_token_counts=0,
                                                                sentence_scores=sentence_scores)

            else:
                return self.parse_sentence_tokens_with_pos_tags(sentence_tokens[1:], current_token,
                                                                intensified_by, negated, has_not,
                                                                part_acum_score, part_token_counts,
                                                                sentence_scores)

    def parse_sentence_tokens_with_pos_tags_by_count(self, sentence_tokens):
        pos = []
        neg = []

        for sentence_token in sentence_tokens:
            current_pos_tag = sentence_token[1]
            current_word = sentence_token[0]

            if self.PATTERN_AVNR.search(current_pos_tag):
                current_word, current_pos_tag = self.stem(current_word.lower(), current_pos_tag)
                if current_word.startswith('anti-'):
                    try:
                        current_score = self._lexicon['n'][current_word]
                    except:
                        current_word = current_word.split('-')[1]
                        current_score = self._lexicon['n'].get(current_word, 0.) * -1
                else:
                    current_score = self._lexicon[current_pos_tag].get(current_word, 0.)
            elif current_pos_tag in {'E', 'G'}:
                current_score = self._lexicon['emoji'].get(current_word.decode('utf-8'))
                current_score = self._lexicon['e'].get(current_word) if not current_score else current_score

            else:
                continue

            if current_score > 0.:
                pos.append(current_word)
            if current_score < 0.:
                neg.append(current_word)

        return 'pos' if len(pos) > len(neg) else ('neg' if len(pos) < len(neg) else 'neu'), pos, neg


    def stem(self, word, pos, type='nltk'):
        # stemming a, v, n, r

        if type == 'wn':
            return (self._nltk_stemmer.lemmatize(word, pos), pos)

        elif type == 'nltk':
            for base_pos in self.POS_SWITCH:
                if base_pos in pos:
                    wn_pos = self.POS_SWITCH[base_pos]
                    try:
                        stemed = self._nltk_stemmer.lemmatize(word, wn_pos)
                    except:
                        stemed = 'asdhoijakls'
                    return (stemed, wn_pos)
                    # else:
                    #     return (self._nltk_stemmer.lemmatize(word, wn_pos), wn_pos) if base_pos != pos else (word, wn_pos)
        else:
            return (None, None)

    def set_lexicon(self, lexicon='swn3'):
        if lexicon == 'swn3':
            if self._lexicon:
                self._lexicon.update(self.load_lexicon_swn3())
            else:
                self._lexicon = self.load_lexicon_swn3()
            # self._lexicon_adj = self._lexicon['a']
            # self._lexicon_adv = self._lexicon['r']
            # self._lexicon_noun = self._lexicon['n']
            # self._lexicon_verb = self._lexicon['v']
        return self

    def parse_tweet(self, text):
        if isinstance(text, list):
            self.POS_SWITCH = {'A': wordnet.ADJ,
                               'V': wordnet.VERB,
                               'N': wordnet.NOUN,
                               'R': wordnet.ADV}
            self.PATTERN_AVNR = re.compile('|'.join(self.POS_SWITCH.keys()))
            for replace in self._replace_list:
                pattern = re.compile(r'(' + '|'.join(
                    [re.escape(key) for key in self.reversed_by(replace)]) + ')')
                text = [pattern.sub(lambda x: replace[x.group()], txt) for txt in text]
            postags = self.postagger_CMU(text)
            # print postags
            return [self.parse_sentence_tokens_with_pos_tags(item) for item in postags]
        else:
            return self.parse_tweet([text])

    def parse_tweet_by_count(self, text):
        if isinstance(text, list):
            self.POS_SWITCH = {'A': wordnet.ADJ,
                               'R': wordnet.ADV}
            self.PATTERN_AVNR = re.compile('|'.join(self.POS_SWITCH.keys()))
            for replace in self._replace_list:
                pattern = re.compile(r'(' + '|'.join(
                    [re.escape(key) for key in self.reversed_by(replace)]) + ')')
                text = [pattern.sub(lambda x: replace[x.group()], txt) for txt in text]
            postags = self.postagger_CMU(text)
            # print postags
            return [self.parse_sentence_tokens_with_pos_tags_by_count(item) for item in postags]
        else:
            return self.parse_tweet_by_count([text])

    @staticmethod
    def postagger_CMU(text_list):
        return runtagger_parse(text_list)

    @staticmethod
    def load_lexicon_swn3():
        from nltk.corpus import sentiwordnet
        swn3 = {'a': dict(), 'n': dict(), 'r': dict(), 'v': dict()}  #adj, noun, adv, verb
        with open(sentiwordnet.abspath('SentiWordNet_3.0.0.txt'), 'r') as i:
            for line in i:
                line = line.strip()
                if line.startswith('#'):
                    continue
                line = line.split('\t')
                for term in line[4].split():
                    term = term.split('#')[0]
                    score = (float(line[2]) - float(line[3])) * 5
                    if term in swn3[line[0]]:
                        swn3[line[0]][term].append(score)
                    else:
                        swn3[line[0]][term] = [score]
        swn3 = dict(map(lambda (p, d):
                        (p, dict(map(lambda (k, v): (k, float(sum(v)) / len(v) if v else 0), ([k,d[k]] for k in d)))),
                        ([p, swn3[p]] for p in swn3)))
        return swn3

    @staticmethod
    def load_lexicon(fp_in, multiplier=1):
        with open(fp_in, 'r') as i:
            lexicon = dict(map(lambda(w, s): (w, float(s) * multiplier), (line.strip().split('\t') for line in i)))
        return lexicon

    def add_lexicon(self, lexicon, sublexicon=None):
        if sublexicon:
            if self._lexicon.has_key(sublexicon):
                self._lexicon[sublexicon].update(lexicon)
            else:
                self._lexicon[sublexicon] = lexicon
        else:
            self._lexicon.update(lexicon)
        return self

    @staticmethod
    def load_list(fp_in):
        with open(fp_in, 'r') as i:
            l = list(set([line.strip('\n') for line in i]))
        return l

    @staticmethod
    def load_replace(fp_in):
        with open(fp_in, 'r') as i:
            replace = dict(map(lambda(w, s): (w, s), (line.strip('\n').split('\t') for line in i)))
        return replace

    def add_replace(self, replace):
        if isinstance(replace, str):
            if replace == 'twillform':
                illformed = dict()
                with open(os.path.join(self.PATH, 'lexicon/corpus.v1.2.tweet'), 'r') as i:
                    csvreader = csv.reader(i, delimiter='\t')
                    for row in csvreader:
                        if len(row) == 3 and row[1] == 'OOV':
                            illformed[row[0]] = row[2]
                return self.add_replace(illformed)

        elif isinstance(replace, dict):
            self._replace_list.insert(0, replace)
        else:
            warnings.warn('ReplaceTypeError')
        return self

    @staticmethod
    def reversed_by(target, key=len):
        if isinstance(target, dict):
            return sorted(target.keys(), key=key, reverse=True)
        if isinstance(target, list):
            return sorted(target, key=key, reverse=True)

    @staticmethod
    def get_avg_score(part_accum_score, part_counts, intensified_by, negation, has_not):
        part_accum_score = part_accum_score * intensified_by * negation
        if has_not == -1:
            part_accum_score += 4. if part_accum_score < 0 else -4
        return part_accum_score / part_counts if part_counts else 0

    def wordcount(self, text):
        ignore = [',', 'P', '~', '#', '&', '@', '^', 'U', '$', 'L']
        ignore = frozenset(ignore)
        avnr = ['A', 'V', 'N', 'R']
        avnr = frozenset(avnr)
        if isinstance(text, list):
            self.POS_SWITCH = {'A': wordnet.ADJ,
                               'V': wordnet.VERB,
                               'R': wordnet.ADV}
            self.PATTERN_AVNR = re.compile('|'.join(self.POS_SWITCH.keys()))
            self._lexicon_emoticons = self.load_lexicon(os.path.join(self.PATH, 'lexicon/emoticons.lex'), 5)
            self._lexicon['e'] = self._lexicon_emoticons
            for replace in self._replace_list:
                pattern = re.compile(r'\b(' + r'|'.join(
                    [re.escape(key) for key in self.reversed_by(replace)]) + r')\b')
                text = [pattern.sub(lambda x: replace[x.group()], txt.lower()) for txt in text]
            sentences = self.postagger_CMU(text)

            counts = dict()
            for tags in sentences:
                for tag in tags:
                    if tag[0].lower() in self.STOP_WORDS:
                        continue
                    if tag[1] in ignore:
                        continue

                    try:
                        word = tag[1] + '_' + (self.stem(tag[0], tag[1].lower(), 'wn')[0] if tag[1] in avnr else tag[0])
                    except UnicodeDecodeError:
                        word = tag[1] + '_' + tag[0]

                    if word in counts:
                        counts[word] += 1
                    else:
                        counts[word] = 1
            return counts
        else:
            return self.wordcount([text])

