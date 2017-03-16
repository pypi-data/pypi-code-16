import MySQLdb
import MySQLdb.cursors

from . import parse_source_path


class MysqlReader(object):
    def __init__(self, source_path):
        self.source_path = source_path
        self.sql_statement = "SELECT {columns} FROM {table} {condition}"
        self.connection = None

    def read(self):
        args = parse_source_path(self.source_path)
        self.connection = MySQLdb.connect(host=args["host"],
                                          user=args["user"],
                                          db=args["database"],
                                          passwd=args["password"],
                                          port=int(args["port"]))
        sql_statement = self.sql_statement.format(columns=args.get("columns"),
                                                  table=args.get("table"),
                                                  condition='WHERE ' + args.get("condition") if args.get("condition")  else '')
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor) if args.get("return_as") else self.connection.cursor()
        print sql_statement
        cursor.execute(sql_statement)
        return cursor.fetchall()

