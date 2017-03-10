#!/usr/local/bin/python
""" Magic Reader geather common files/urls extantions with the exact same command. """

from retrying import retry
from fake_useragent import UserAgent

import unicodecsv as csv
import ujson
import yaml
import MySQLdb
import requests
import psycopg2


SUPPORTED_TYPES = ['txt', 'yml', 'yaml', 'json', 'csv', 'mysql', 'postgres', 'request']


class MissingParametersException(Exception):
    pass


class NotValidFileTypeException(Exception):
    pass


class NoSupportedOperationException(Exception):
    pass


class FetchModeConflictException(Exception):
    pass


class Open(object):

    def __init__(self, data_source_path):
        self.data_source_path = data_source_path


    def __enter__(self):

        self.file_type = self.data_source_path.split('.')[-1]
        self.__data = None
        self.sql_statement = "SELECT {fields} FROM {table} {where_clause}"

        if '.' not in self.data_source_path:
            raise NotValidFileTypeException("Please add the type of the file.")
        if self.file_type not in SUPPORTED_TYPES:
            raise NotValidFileTypeException("The current suffix is not yet supported.")

        self.__create_reader_based_on_file_type()
        return self.__data

    def __create_reader_based_on_file_type(self):
        if self.file_type == 'txt':
            self.validate_file_existence()
            self.__data = self.__text_read()
        elif self.file_type == 'json':
            self.validate_file_existence()
            self.__json_read()
        elif self.file_type == 'csv':
            self.validate_file_existence()
            self.__data = self.__csv_read()
        elif self.file_type in ('yml', 'yaml'):
            self.validate_file_existence()
            self.__yml_read()
        elif self.file_type == 'mysql':
            self.__mysql_read()
        elif self.file_type == 'postgres':
            self.__postgres_read()
        elif self.file_type == 'request':
            self.__request_read()

    def validate_file_existence(self):
        try:
            with open(self.data_source_path, "rb") as f_path_check:
                pass
        except IOError as error:
            raise IOError("The data source path you specified not found.")

    def __text_read(self):
        text_reader = open(self.data_source_path, "rb")
        for line in text_reader:
            yield line

        text_reader.close()

    def __json_read(self):
        with open(self.data_source_path, "rb") as json_reader:
            self.__data = ujson.load(json_reader)

    def __csv_read(self):
        file_reader = open(self.data_source_path, "rb")
        csv_reader = csv.reader(file_reader)
        for line in csv_reader:
            yield line

        file_reader.close()

    def __yml_read(self):
        with open(self.data_source_path, "rb") as text_reader:
            self.__data = yaml.load(text_reader)

    def __mysql_read(self):
        arguments = self.__parse_db_arguments()
        conn = MySQLdb.connect(host=arguments["host"],
                               user=arguments["user"],
                               db=arguments["db"],
                               passwd=arguments["password"],
                               port=arguments["port"])
        cur = conn.cursor()
        stmt = self.sql_statement.format(fields=arguments["fields"],
                                         table=arguments["table"],
                                         where_clause=arguments["condition"])
        cur.execute(stmt)
        self.__data = iter(cur)

    def __postgres_read(self):
        arguments = self.__parse_db_arguments()
        conn = psycopg2.connect(host=arguments["host"],
                                user=arguments["user"],
                                database=arguments["db"],
                                password=arguments["password"],
                                port=arguments["port"])
        cur = conn.cursor()
        stmt = self.sql_statement.format(fields=arguments["fields"],
                                         table=arguments["table"],
                                         where_clause=arguments["condition"])
        cur.execute(stmt)
        self.__data = iter(cur)

    def __request_read(self):
        arguments = self.__parse_request_arguments()
        @retry(stop_max_attempt_number=arguments["num_of_retries"],
               wait_fixed=arguments["wait_between_retries"])
        def fetch():
            ua = UserAgent(cache=True)
            if arguments["stream"] and arguments["read_as"] == "json":
                raise FetchModeConflictException("Streaming this source is only"
                                                 " available when fetching content as text.")
            elif arguments["stream"]:
                s = getattr(requests, arguments["method"])(arguments["url"], headers={'User-Agent': ua.google}, stream=True)
                if s.status_code == 200:
                        self.__data = s.iter_content()
            else:
                s = getattr(requests, arguments["method"])(arguments["url"], headers={'User-Agent': ua.google})
                self.__data = getattr(s, arguments["read_as"])() if arguments["read_as"] == "json" else getattr(s, arguments["read_as"])

        fetch()

    def __parse_db_arguments(self):
        arguments = self.data_source_path.split('::')
        if len(arguments) < 6:
            raise MissingParametersException("One or more parameter is missing.")
        host = arguments[0]
        user = arguments[1]
        passwd = arguments[2]
        port = arguments[3]
        db, table = arguments[4].split(".")[0], arguments[4].split(".")[1]
        fields = arguments[5].split(".")[0]
        where_caluse = ''
        if len(arguments) >= 7:
            if "[" in arguments[6]:
                where_caluse = arguments[6].split("].")[0].replace("[", "")

        return dict(host=host, user=user, password=passwd,
                    port=int(port), db=db, table=table, fields=fields,
                    condition=where_caluse)

    def __parse_request_arguments(self):
        arguments = self.data_source_path.split("::")
        if len(arguments) < 5:
            raise MissingParametersException("One or more parameter is missing.")
        method = arguments[0]
        url = arguments[1]
        read_as = arguments[2]
        num_of_retries = int(arguments[3])
        wait_between_retries = int(arguments[4].split('s')[0]) * 1000  # in seconds.
        stream = False
        if len(arguments) == 6:
            stream = True if arguments[5].split('.')[0] == "stream" else False

        return dict(method=method, url=url,
                    read_as=read_as, num_of_retries=num_of_retries,
                    wait_between_retries=wait_between_retries, stream=stream)

    def __exit__(self, type, value, traceback):
        pass

if __name__ == '__main__':
    with Open("/Users/benny/readP/tests/test.json") as reader:
        pass
        # Do whatever you wish with your reader (be aware the type according to the file you open.)
        # txt = iterator
        # csv = iterator
        # json = dict
        # yml = dict
        # dbs = iterator
        # request = depends on your request.
