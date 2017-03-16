import psycopg2
import psycopg2.extras

from . import parse_source_path


class PostgresReader(object):
    def __init__(self, source_path):
        self.source_path = source_path
        self.sql_statement = "SELECT {columns} FROM {table} {condition}"
        self.connection = None

    def read(self):
        args = parse_source_path(self.source_path)
        self.connection = psycopg2.connect(host=args["host"],
                                           user=args["user"],
                                           database=args["database"],
                                           password=args["password"],
                                           port=args["port"])
        sql_statement = self.sql_statement.format(columns=args.get("columns"),
                                                  table=args.get("table"),
                                                  condition='WHERE ' + args.get("condition") if args.get("condition") else '')
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) if args.get("return_as") else self.connection.cursor()
        cursor.execute(sql_statement)
        return cursor.fetchall()
