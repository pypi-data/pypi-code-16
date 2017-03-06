# -*- coding: utf-8 -*-
import io
from nltk.tokenize import punkt
from nltk.tokenize.punkt import PunktLanguageVars

from pynlple.data.corpus import StackingSource, FilteringSource, JsonFieldSource, MappingSource, \
    OpensubtitlesSentenceSource, FileLineSource
from pynlple.data.filesource import FilePathSource
from pynlple.data.jsonsource import FileJsonDataSource
from pynlple.processing.preprocessor import DefaultPreprocessorStack, RegexReplacerAdapter, StackingPreprocessor
from pynlple.module import abs_path, append_paths
import re


class YSMultiLangVars(PunktLanguageVars):

    def __init__(self):
        super().__init__()
        self.default_replacers = DefaultPreprocessorStack()
        self.period_reverter = RegexReplacerAdapter(r'\s(\.)', r'\1', False, False, True)
        self.preprocessor_tokenizer = StackingPreprocessor([self.default_replacers, self.period_reverter])

    def word_tokenize(self, s):
        return self.preprocessor_tokenizer.preprocess(s).split()


path1 = 'F:/text_lang/'
path2 = 'F:/data/youscan/mentions/2016.12.09-I_lang/'
path3 = 'E:/data/youscan/mentions/2016.12.09-II_lang/'
path4 = 'E:/data/youscan/mentions/2016.12.09-III_lang/'

facebook_looksmi_source = StackingSource([FileJsonDataSource(path) for path in FilePathSource([path1])])
language_facebook_looksmi_source = FilteringSource(facebook_looksmi_source, lambda j: j['lang'] in ['rus'])
text_facebook_looksmi_source = JsonFieldSource(language_facebook_looksmi_source, 'Text')

youscan_source = StackingSource([FileJsonDataSource(path) for path in FilePathSource([path2, path3, path4])])
language_youscan_source = FilteringSource(youscan_source, lambda j: j['lang'] in ['rus'])
text_youscan_source = JsonFieldSource(youscan_source, 'text')

opensub_file = 'F:/corpora/OpenSubtitles/OpenSubtitles2016.raw.ru'
dash_at_start_remover = RegexReplacerAdapter(r'-\s', '', False, False, True)
opensub_sentences = OpensubtitlesSentenceSource(MappingSource(FileLineSource(opensub_file, encoding='utf8'), dash_at_start_remover.preprocess))

all_text_source = StackingSource([text_facebook_looksmi_source, text_youscan_source, opensub_sentences])

line_source = StackingSource(MappingSource(all_text_source, lambda t: re.split(r'[\r\n]+', t)))
# line_source = MappingSource(line_source, lambda l: l.replace('кг.', 'кг!'))
# token_source = MappingSource(line_source, lambda t: replacers_stack.preprocess(t))

trainer = punkt.PunktTrainer()
for line in line_source:
    trainer.train(line, verbose=False, finalize=False)

trainer.finalize_training()
model = trainer.get_params()

import pickle
model_path = append_paths(abs_path('model/'), 'fb-smi-ys-OS.psm')
with io.open(model_path, mode='wb') as fout:
    pickle.dump(model, fout, protocol=pickle.HIGHEST_PROTOCOL)
# #
# with io.open(model_path, mode='rb') as fin:
#     model = pickle.load(fin)
#
# splitter = punkt.PunktSentenceTokenizer(model)

i = 0
for line in line_source:
    # for sent in splitter.tokenize(line):
    #     print(sent)
    print('---')
    i += 1
    if i > 100:
        break
