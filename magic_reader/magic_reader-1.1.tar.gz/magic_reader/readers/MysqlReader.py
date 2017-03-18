import MySQLdb
import MySQLdb.cursors

from . import parse_source_path


class MysqlReader(object):

    connection_args = dict()

    def __init__(self, source_path):
        self.source_path = source_path
        self.connection = None
        args = parse_source_path(self.source_path)

        # Connection parse.
        self.connection_args.setdefault("host", args.get("host"))
        self.connection_args.setdefault("user", args.get("user"))
        self.connection_args.setdefault("db", args.get("db"))
        self.connection_args.setdefault("passwd", args.get("password"))
        self.connection_args.setdefault("port", 3306 if not args.get("port") else int(args.get("port")))

        # Sql parse.
        self.sql_statement = "SELECT {columns} FROM {table} {condition}"
        self.columns = args.get("columns")
        self.table = args.get("table")
        self.condition = "" if not args.get("condition") else "WHERE " + args.get("condition")

        # Return as
        self.return_results_as = "" if not args.get("return_as") else args.get("return_as")

    def read(self):
        self.connection = MySQLdb.connect(**self.connection_args)
        sql_statement = self.sql_statement.format(columns=self.columns, table=self.table, condition=self.condition)
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor) if self.return_results_as else self.connection.cursor()
        cursor.execute(sql_statement)
        return cursor.fetchall()

