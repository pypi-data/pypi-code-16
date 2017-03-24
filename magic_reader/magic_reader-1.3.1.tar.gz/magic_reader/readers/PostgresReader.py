import psycopg2
import psycopg2.extras

from . import parse_source_path


class PostgresReader(object):

    connection_args = dict()

    def __init__(self, source_path, real_path=None):
        self.source_path = source_path
        self.connection = None
        args = parse_source_path(self.source_path)
        # Connection parse.
        self.connection_args = dict()
        self.connection_args.setdefault("host", args.get("host"))
        self.connection_args.setdefault("user", args.get("user"))
        self.connection_args.setdefault("database", args.get("database"))
        self.connection_args.setdefault("password", args.get("password"))
        self.connection_args.setdefault("port", 5432 if not args.get("port") else int(args.get("port")))
        try:
            self.connection = psycopg2.connect(**self.connection_args)
        except Exception as err:
            raise err
        # Sql parse.
        self.sql_statement = "SELECT {columns} FROM {table} {condition}"
        self.columns = args.get("columns")
        self.table = args.get("table")
        self.condition = "" if not args.get("condition") else "WHERE " + args.get("condition")

        # Return as
        self.return_results_as = "" if not args.get("return_as") else args.get("return_as")

    def read(self):
        sql_statement = self.sql_statement.format(columns=self.columns, table=self.table, condition=self.condition)
        cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor) if self.return_results_as else self.connection.cursor()
        cursor.execute(sql_statement)
        return (row for row in cursor.fetchall())


