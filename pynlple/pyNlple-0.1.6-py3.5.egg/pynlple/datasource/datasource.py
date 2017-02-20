# -*- coding: utf-8 -*-
import csv

import io
import json

from pandas import read_csv
from pandas import DataFrame

from pynlple.exceptions import DataSourceException
from pynlple.datasource.filesource import FilePathSource
from pynlple.module import append_paths, file_name


class Source(object):

    def __repr__(self, *args, **kwargs):
        return '{}({})'.format(str(self.__class__.__name__), repr(vars(self)))


class SkippingSource(Source):

    def __init__(self):
        self.__to_skip = None
        self.__to_take = None
        super().__init__()

    def to_skip(self):
        return self.__to_skip

    def skip(self, skip):
        self.__to_skip = skip
        return self

    def to_take(self):
        return self.__to_take

    def take(self, take):
        self.__to_take = take
        return self


class BulkSource(SkippingSource):

    def __init__(self, skipping_source, bulk_size=5000):
        self.skipping_source = skipping_source
        self.bulk = bulk_size
        super().__init__()

    def get_data(self):
        all_data = []
        range_ = self.__get_bulk_range_limited(self.to_skip() if self.to_skip() else 0, len(all_data))
        try:
            got = None
            print('Start draining from skipping source: {}'.format(repr(self.skipping_source)))
            while range_ and (not got or got >= self.bulk):
                data = self.__get_bulk(range_)
                got = len(data)
                all_data.extend(data)
                range_ = self.__get_bulk_range_limited(range_[1], len(all_data))
            print('Source seems to be exhausted')
            return all_data
        except DataSourceException as de:
            raise DataSourceException('Error while dumping bulk {}-{} from {}:\n{}'.format(str(range_[0]), str(range_[1]), repr(self), de.__str__()))

    def __get_bulk_range_limited(self, init_s, got_total):
        real_bulk = self.bulk
        # If there are limits on amount to take, check if we reached them
        if self.to_take():
            to_limit_leftover = self.to_take() - got_total
            # Reduce the bulk to the leftover amount
            if real_bulk > to_limit_leftover:
                real_bulk = to_limit_leftover
        # If we are not going to take anything in the end - return None
        if real_bulk == 0:
            return None
        else:
            return init_s, init_s + real_bulk

    def __get_bulk(self, bulk_range_tuple):
        print('Getting {}-{} bulk from the skipping source'.format(str(bulk_range_tuple[0]), str(bulk_range_tuple[1])))
        data = self.skipping_source.skip(bulk_range_tuple[0]).take(bulk_range_tuple[1] - bulk_range_tuple[0]).get_data()
        return data


class DataframeSource(Source):

    def __init__(self, dataframe):
        self.dataframe = dataframe

    def get_dataframe(self):
        return self.dataframe

    def set_dataframe(self, dataframe):
        self.dataframe = dataframe


class TsvDataframeSource(Source):

    def __init__(self, dataframe_path, separator='\t', fill_na_map=None, encoding='utf8', index_column='id'):
        self.path = dataframe_path
        self.separator = separator
        self.na_map = fill_na_map
        self.encoding = encoding
        self.index_column = index_column

    def get_dataframe(self):
        dataframe = read_csv(self.path, sep=self.separator, quoting=csv.QUOTE_NONE, encoding=self.encoding)
        dataframe.set_index(self.index_column, inplace=True)
        if self.na_map:
            for key, value in self.na_map.items():
                dataframe[key].fillna(value, inplace=True)
        print('Read: ' + str(len(dataframe.index)) + ' rows from ' + self.path)
        return dataframe

    def set_dataframe(self, dataframe):
        dataframe.to_csv(self.path, sep=self.separator, quoting=csv.QUOTE_NONE, encoding=self.encoding)
        print('Write: ' + str(len(dataframe.index)) + ' rows to ' + self.path)


class TsvFolderDataframeSource(Source):

    SOURCE_COLUMN_NAME = 'source_filepath'

    def __init__(self, folder_path, extension_suffix='.tsv', separator='\t', fill_na_map=None, encoding='utf8'):
        self.path = folder_path
        self.extension = extension_suffix
        self.separator = separator
        self.na_map = fill_na_map
        self.encoding = encoding

    def get_dataframe(self):
        dataframe = DataFrame()
        for filepath in FilePathSource.iter_folder_filepaths(self.path, self.extension):
            subframe = TsvDataframeSource(self.path, self.separator, self.na_map, self.encoding).get_dataframe()
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

    FILE_OPEN_METHOD = 'rt'
    FILE_WRITE_METHOD = 'wt'
    DEFAULT_ENCODING = 'utf8'

    def __init__(self, json_file_path, keys=None, fill_na_map=None, index_column='id'):
        self.json_file_path = json_file_path
        self.keys = keys
        self.na_map = fill_na_map
        self.index_column = index_column

    def set_dataframe(self, dataframe):
        with io.open(self.json_file_path, JsonFileDataframeSource.FILE_WRITE_METHOD, encoding=JsonFileDataframeSource.DEFAULT_ENCODING) as data_file:
            json.dump(dataframe.reset_index().to_dict(orient='records'), data_file, ensure_ascii=False, indent=2)


class JsonDataframeSource(Source):

    def __init__(self, json_source, keys=None, fill_na_map=None, index_column='id'):
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

