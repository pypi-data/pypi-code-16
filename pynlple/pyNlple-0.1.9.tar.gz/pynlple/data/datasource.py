# -*- coding: utf-8 -*-
import csv
import io
import json

from pandas import DataFrame
from pandas import read_csv, read_json

from pynlple.data.filesource import FilePathSource
from pynlple.data.source import Source
from pynlple.module import append_paths, file_name


class DataframeSource(Source):

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_dataframe(self):
        return self.dataframe

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe


class TsvDataframeSource(Source):

    def __init__(self, dataframe_path, separator='\t', column_names=None, fill_na_map=None, encoding='utf8', index_column='uid'):
        self.path = dataframe_path
        self.separator = separator
        self.column_names = column_names
        self.na_map = fill_na_map
        self.encoding = encoding
        self.index_column = index_column

    def get_dataframe(self):
        if self.column_names:
            header = None
            names = self.column_names
        else:
            header = 'infer'
            names = None
        dataframe = read_csv(self.path,
                             sep=self.separator,
                             header=header,
                             names=names,
                             quoting=csv.QUOTE_NONE,
                             escapechar='\\',
                             encoding=self.encoding)
        if self.index_column:
            dataframe.set_index(self.index_column, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from ' + self.path)
        return dataframe

    def set_dataframe(self, dataframe):
        if self.column_names:
            names = self.column_names
        else:
            names = True
        dataframe.to_csv(self.path,
                         sep=self.separator, header=names, quoting=csv.QUOTE_NONE, escapechar='\\',
                         encoding=self.encoding)
        print('Write: ' + str(len(dataframe.index)) + ' rows to ' + self.path)


class TsvFolderDataframeSource(Source):

    SOURCE_COLUMN_NAME = 'source_filepath'

    def __init__(self, folder_path, extension_suffix='.tsv', separator='\t', column_names=None, fill_na_map=None, encoding='utf8', index_column='uid'):
        self.path = folder_path
        self.extension = extension_suffix
        self.separator = separator
        self.column_names = column_names
        self.na_map = fill_na_map
        self.encoding = encoding
        self.index_column = index_column

    def get_dataframe(self):
        dataframe = DataFrame()
        for filepath in FilePathSource(self.path, self.extension):
            subframe = TsvDataframeSource(self.path,
                                          separator=self.separator,
                                          column_names=self.column_names,
                                          fill_na_map=self.na_map,
                                          encoding=self.encoding,
                                          index_column=self.index_column).get_dataframe()
            subframe[TsvFolderDataframeSource.SOURCE_COLUMN_NAME] = filepath
            dataframe = dataframe.append(subframe)
        return dataframe

    def set_dataframe(self, dataframe):
        for filepath in dataframe[TsvFolderDataframeSource.SOURCE_COLUMN_NAME].unique():
            subframe = dataframe.loc[TsvFolderDataframeSource.SOURCE_COLUMN_NAME == filepath]
            subframe.drop([TsvFolderDataframeSource.SOURCE_COLUMN_NAME], inplace=True, axis=1, errors='ignore')
            filename = file_name(filepath)
            new_path = append_paths(self.path, filename)
            TsvDataframeSource(new_path, self.separator, self.encoding).set_dataframe(subframe)


class JsonFileDataframeSource(Source):

    FILE_READ_METHOD = 'rt'
    FILE_WRITE_METHOD = 'wt'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, json_file_path, keys=None, fill_na_map=None, index_column='uid'):
        self.json_file_path = json_file_path
        self.keys = keys
        self.na_map = fill_na_map
        self.index_column = index_column

    def get_dataframe(self):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_READ_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            df = read_json(data_file, orient='records', encoding=JsonFileDataframeSource.DEFAULT_ENCODING)
        return df

    def set_dataframe(self, dataframe):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_WRITE_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            json.dump(dataframe.reset_index().to_dict(orient='records'), data_file, ensure_ascii=False, indent=2)


class JsonDataframeSource(Source):

    def __init__(self, json_source, keys=None, fill_na_map=None, index_column='uid'):
        self.json_source = json_source
        self.keys = keys
        self.na_map = fill_na_map
        self.index_column = index_column

    def get_dataframe(self):
        extracted_entries = list()
        for json_object in self.json_source.get_data():
            entry = dict()
            if self.keys:
                for key in self.keys:
                    if key not in json_object:
                        entry[key] = self.na_map[key]
                    else:
                        entry[key] = json_object[key]
            else:
                for key in json_object:
                    entry[key] = json_object[key]
                if self.na_map:
                    for key, value in self.na_map:
                        if key not in entry:
                            entry[key] = value
            extracted_entries.append(entry)
        dataframe = DataFrame(extracted_entries)
        dataframe.set_index(self.index_column, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from jsonsource')
        return dataframe

    def set_dataframe(self, dataframe):
        entries = dataframe.reset_index().to_dict(orient='records')
        for entry in entries:
            if self.keys:
                for key in list(entry.keys()):
                    if key not in self.keys:
                        entry.pop(key, None)
            if self.na_map:
                for key, value in self.na_map:
                    if key not in entry:
                        entry[key] = value
        self.json_source.set_data(entries)

