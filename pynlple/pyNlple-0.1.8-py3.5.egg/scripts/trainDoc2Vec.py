# -*- coding: utf-8 -*-
import logging

import itertools
import re

from gensim.models.doc2vec import TaggedDocument

from pynlple.data.corpus import StackingSource, FilteringSource, JsonFieldSource, MappingSource, \
    OpensubtitlesSentenceSource, FileLineSource, SplittingSource
from pynlple.data.filesource import FilePathSource
from pynlple.data.jsonsource import FileJsonDataSource
from pynlple.processing.preprocessor import DefaultPreprocessorStack, RegexReplacerAdapter
from pynlple.module import abs_path, append_paths
from gensim import models

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

replacers_stack = DefaultPreprocessorStack()

path1 = 'F:/text_lang/'
path2 = 'F:/data/youscan/mentions/2016.12.09-I_lang/'
path3 = 'F:/data/youscan/mentions/2016.12.09-II_lang/'
path4 = 'F:/data/youscan/mentions/2016.12.09-III_lang/'

facebook_looksmi_source = StackingSource([FileJsonDataSource(path) for path in FilePathSource([path1])], log=True)
language_facebook_looksmi_source = FilteringSource(facebook_looksmi_source, lambda j: j['lang'] in ['rus'])
text_facebook_looksmi_source = JsonFieldSource(language_facebook_looksmi_source, 'Text')

youscan_source = StackingSource([FileJsonDataSource(path) for path in FilePathSource([path2, path3, path4])], log=True)
language_youscan_source = FilteringSource(youscan_source, lambda j: j['lang'] in ['rus'])
text_youscan_source = JsonFieldSource(youscan_source, 'text')

opensub_file = 'F:/corpora/OpenSubtitles/OpenSubtitles2016.raw.ru'
dash_cleaner = RegexReplacerAdapter(r'(^-\s)|(-+$)', '', False, False, True)
opensub_sentences = OpensubtitlesSentenceSource(MappingSource(FileLineSource(opensub_file, encoding='utf8'), dash_cleaner.preprocess))

all_text_source = StackingSource([text_facebook_looksmi_source, text_youscan_source, opensub_sentences])

line_source = SplittingSource(all_text_source, lambda t: re.split(r'[\r\n]+', t))
token_source = MappingSource(line_source, lambda t: replacers_stack.preprocess(t).split())

n = 3
long_sentences_source = FilteringSource(token_source, lambda s: len(s) >= n)

source = MappingSource(long_sentences_source, lambda s: TaggedDocument(s, (str(hash(tuple(s))),)))
key = 'facebook' + '_min_tokens=' + str(n)
pars = dict(
    size=400,
    window=8,
    dm=1,
    dbow_words=1,
    dm_mean=1,
    negative=5,
    seed=13,
    min_count=2,
    iter=10,
    workers=3
)
params = '_'.join(repr(key) + '=' + repr(pars[key]) for key in sorted(pars.keys()))
vocab_name = 'gensim_doc2vec_' + key + '_' + params + '.voc'
vocab_path = append_paths(abs_path('model/'), vocab_name)
model_name = 'gensim_doc2vec_' + key + '_' + params + '.tst'
model_path = append_paths(abs_path('model/'), model_name)

model = models.Doc2Vec(None, **pars)
model.scan_vocab(source, progress_per=25000, trim_rule=None, update=False)
model.save(vocab_path)
print('Vocabulary building step finished. Vocabulary saved.')
# print('Loading vocabulary.')
# model = models.Doc2Vec.load(vocab_path)

model.scale_vocab(keep_raw_vocab=True, trim_rule=None, update=False)
model.finalize_vocab(update=False)
model.train(source)
model.save(model_path)
print('First training step finished.')

# model = models.Doc2Vec.load(model_path)
# print ('Model ' + model_name + ' was successfully loaded.')