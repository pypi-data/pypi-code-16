# -*- coding: utf-8 -*-
import logging
import re

from pynlple.data.corpus import StackingSource, FilteringSource, JsonFieldSource, MappingSource, \
    OpensubtitlesSentenceSource, FileLineSource
from pynlple.data.filesource import FilePathSource
from pynlple.data.jsonsource import FileJsonDataSource
from pynlple.processing.preprocessor import DefaultPreprocessorStack, RegexReplacerAdapter
from pynlple.module import abs_path, append_paths
from gensim import models

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

replacers_stack = DefaultPreprocessorStack()

path1 = 'F:/text_lang/'
path2 = 'F:/data/youscan/mentions/2016.12.09-I_lang/'
path3 = 'F:/data/youscan/mentions/2016.12.09-II_lang/'
path4 = 'F:/data/youscan/mentions/2016.12.09-III_lang/'

facebook_looksmi_source = StackingSource([FileJsonDataSource(path) for path in FilePathSource([path1])])
language_facebook_looksmi_source = FilteringSource(facebook_looksmi_source, lambda j: j['lang'] in ['rus'])
text_facebook_looksmi_source = JsonFieldSource(language_facebook_looksmi_source, 'Text')

youscan_source = StackingSource([FileJsonDataSource(path) for path in FilePathSource([path2, path3, path4])])
language_youscan_source = FilteringSource(youscan_source, lambda j: j['lang'] in ['rus'])
text_youscan_source = JsonFieldSource(youscan_source, 'text')

opensub_file = 'F:/corpora/OpenSubtitles/OpenSubtitles2016.raw.ru'
dash_cleaner = RegexReplacerAdapter(r'(^-\s)|(-+$)', '', False, False, True)
opensub_sentences = OpensubtitlesSentenceSource(MappingSource(FileLineSource(opensub_file, encoding='utf8'), dash_cleaner.preprocess))

all_text_source = StackingSource([text_facebook_looksmi_source, text_youscan_source, opensub_sentences])

line_source = StackingSource(MappingSource(all_text_source, lambda t: re.split(r'[\r\n]+', t)))
token_source = MappingSource(line_source, lambda t: replacers_stack.preprocess(t).split())

# one_file_path1 = 'F:/text_lang/facebook-text-1.txt'
# one_file_source = FileJsonDataSource(one_file_path1)
# language_one_file_source = FilteringSource(one_file_source, lambda j: j['lang'] in ['rus'])
# text_one_file__source = JsonFieldSource(language_one_file_source, 'Text')
# line_source = StackingSource(MappingSource(text_one_file__source, lambda t: re.split(r'[\r\n]+', t)))
# token_source = MappingSource(line_source, lambda t: replacers_stack.preprocess(t).split())

n = 2
source = FilteringSource(token_source, lambda s: len(s) >= n)

key = 'rus_OS_min_tokens=' + str(n)
pars = dict(
    size=380,
    sg=1,
    hs=1,
    negative=0,
    seed=13,
    min_count=5,
    sample=1e-4,
    iter=5,
    workers=3
)
params = '_'.join(repr(key) + '=' + repr(pars[key]) for key in sorted(pars.keys()))
vocab_name = 'gensim_word2vec_' + key + '_' + params + '.voc'
vocab_path = append_paths(abs_path('model/'), vocab_name)
model_name = 'gensim_word2vec_' + key + '_' + params + '.tst'
model_path = append_paths(abs_path('model/'), model_name)

# model = models.Word2Vec(None, **pars)
# model.scan_vocab(source, progress_per=25000, trim_rule=None, update=False)
# model.save(vocab_path)
# print('Vocabulary building step finished. Vocabulary saved.')
# print('Loading vocabulary.')
# model = models.Word2Vec.load(vocab_path)
#
# model.scale_vocab(keep_raw_vocab=True, trim_rule=None, update=False)
# model.finalize_vocab(update=False)
# model.train(source)
# model.save(model_path)
# print('First training step finished.')

model = models.Word2Vec.load(model_path)
model.init_sims(replace=True)
print('Model ' + model_name + ' was successfully loaded.')
#
# print('Post training step starting.')
#
word = 'привет'
word_replacement = word.split()
# word_replacement = ['1соль1']
#
# altered_source = FilteringSource(source, lambda s: word in s)
# altered_source = MappingSource(altered_source, lambda tokens: [word_replacement if token == word else token for token in tokens])
#
# model.build_vocab(altered_source, update=True)
# model.train(altered_source)
#
print('Post-training step')
if all(w in model.vocab for w in word_replacement):
    similars = model.most_similar(word_replacement, topn=30)
    print(word + ': ' + ', '.join([similar[0] + '>' + str(similar[1]) for similar in similars]))
else:
    print('Word not found.')


