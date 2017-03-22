# -*- coding: utf-8 -*-
from pynlple.data.filesource import FilePathSource
from pynlple.data.jsonsource import FileJsonDataSource
from pynlple.data.datasource import JsonDataframeSource

in_folder_path = 'F:/data/youscan/mentions/2016.12.09-III_lang'
in_extension = '.json'
key_columns = [u'text']
keep = 'last'

filepaths = FilePathSource([in_folder_path], extension_suffix=in_extension)
for filepath in filepaths:
    jsonsource = FileJsonDataSource(filepath)
    dataframesource = JsonDataframeSource(jsonsource)
    dataframe = dataframesource.get_dataframe()
    if 'duplicate' not in dataframe.columns:
        duplicates = dataframe.duplicated(subset=key_columns, keep=keep)
        dataframe['duplicate'] = duplicates

        dataframesource.set_dataframe(dataframe)
