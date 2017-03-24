#!/usr/local/bin/python

from readers.JsonReader import JsonReader
from readers.MysqlReader import MysqlReader
from readers.RequestReader import RequestReader
from readers.TextReader import TextReader
from readers.YamlReader import YamlReader
from readers.CsvReader import CsvReader

from readers.PostgresReader import PostgresReader


class ObjectTypeNotSupportedException(Exception):
    pass


class Read(object):

    SUPPORTED_TYPES = ('txt', 'text', 'yml', 'yaml', 'json', 'request', 'csv', 'mysql', 'postgres')
    READERS = dict(
        txt=TextReader,
        text=TextReader,
        yml=YamlReader,
        yaml=YamlReader,
        json=JsonReader,
        mysql=MysqlReader,
        postgres=PostgresReader,
        request=RequestReader,
        csv=CsvReader
    )

    def __init__(self, source_path, object_type):
        self.object_type = object_type
        self.source_path = source_path

    def __enter__(self):

        if self.object_type.lower() not in self.SUPPORTED_TYPES:
            raise ObjectTypeNotSupportedException("Not supported type. {}".format(self.object_type))

        self.object_type = self.object_type.lower()
        self.real_path = "".join(self.source_path.split(" ")).replace("\n", "")
        self.source_path = "".join(self.source_path.lower().split(" ")).replace("\n", "")

        reader_instance = self.__get_reader()

        try:
            return reader_instance.read()
        except Exception as err:
            raise err

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __get_reader(self):
        return self.READERS[self.object_type](self.source_path, self.real_path)
