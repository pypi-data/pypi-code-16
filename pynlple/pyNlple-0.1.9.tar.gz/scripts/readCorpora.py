# -*- coding: utf-8 -*-
import logging
import sys
import re

from pynlple.data.corpus import StackingSource, FilteringSource, JsonFieldSource, MappingSource, \
    OpensubtitlesSentenceSource, FileLineSource
from pynlple.data.filesource import FilePathSource
from pynlple.data.jsonsource import FileJsonDataSource
from pynlple.processing.preprocessor import DefaultPreprocessorStack, RegexReplacerAdapter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger_handler = logging.StreamHandler(sys.stdout)
# logger_handler = logging.FileHandler('readCorpora.log', encoding='utf8', mode='wt')
logger_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
logger_handler.setFormatter(formatter)
logger.addHandler(logger_handler)

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

all_text_source = StackingSource([text_facebook_looksmi_source, text_youscan_source, opensub_sentences], log=True)

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


i = 0
for line in source:
    i += 1
    if i > 100000:
        break
