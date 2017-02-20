# -*- coding: utf-8 -*-
from pynlple.datasource.datasource import TsvDataframeSource
from pynlple.datasource.filesource import FilePathSource
from pynlple.processing.preprocessor import DefaultPreprocessorStack

extension = '.tsv'
key = 'small'
in_folder_path = 'E:/Data/mentions_deduplicated/' + key
out_folder_path = 'E:/Data/mentions_preprocessed/' + key

target_columns = [u'text']

replacers_stack = DefaultPreprocessorStack()

for filepath in FilePathSource.iter_folder_filepaths(in_folder_path, extension):
    dataframe = TsvDataframeSource(filepath, '\t', {u'text': u''}, 'utf8').get_dataframe()

    for target_column in target_columns:
        dataframe[target_column] = dataframe[target_column].apply(replacers_stack.preprocess)

    newpath = filepath.replace(in_folder_path, out_folder_path, 1)
    TsvDataframeSource(newpath, '\t', encoding='utf8').set_dataframe(dataframe)


