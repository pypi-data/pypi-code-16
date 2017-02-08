PARAM_STYLES = {
    'qmark': lambda x: '?',
    'numeric': lambda x: ':%d' % x[0],
    'named': lambda x: ':%s' % x[1],
    'format': lambda x: '%s',
    'pyformat': lambda x: '%%(%s)s' % x[1],
    }


def named_parameters(cols, data):
    return dict(map(lambda x: (x, data[x]), cols))


def sequential_parameters(cols, data):
    return map(lambda x: data[x], cols)


class GenericSQLAdapter(object):
    def __init__(self, db, **kwargs):
        self._connection_opts = kwargs
        self._connection = None
        self._db = db
        self.param = PARAM_STYLES[db.paramstyle]

        if db.paramstyle in ('named', 'pyformat'):
            self.create_parameters = named_parameters
        else:
            self.create_parameters = sequential_parameters

    def cursor(self):
        return self.connection.cursor()

    def insert(self, mapping, obj):
        """Inserts the `obj` instance into database"""

        data = mapping.object_to_dict(obj)
        cols = mapping.data_columns()

        cur = self.cursor()

        sql = '''insert into %s (%s) values (%s)''' % (
            mapping.db_table,
            ','.join(cols),
            ','.join(map(self.param, enumerate(cols)))
        )

        cur.execute(sql, self.create_parameters(cols, data))

    def update(self, mapping, obj):
        """Updates the `obj` instance state in the database"""

        data = mapping.object_to_dict(obj)
        cols = mapping.data_columns()

        cur = self.cursor()

        all_columns = mapping.columns()

        set_params = map(
                lambda x: '%s=%s' % (x[1], self.param(x)), enumerate(cols))

        where_params = map(
                lambda x: '%s=%s' % (x[1], self.param(x)),
                enumerate(mapping.primary_key()))

        sql = '''update %s set %s where %s''' % (
            mapping.db_table,
            ','.join(set_params),
            ' and '.join(where_params),
            )

        cur.execute(sql, self.create_parameters(all_columns, data))

    def select_all(self, mapping, obj_class, limit=None, offset=None):
        cols = mapping.columns()
        sql = 'select %s from %s'

        if offset:
            sql += ' offset %d' % offset

        if limit:
            sql += ' limit %d' % limit

        sql = sql % (','.join(cols), mapping.db_table)

        return self.raw(sql, mapping, obj_class)

    def raw(self, sql, mapping, obj_class):
        """
        Instantiate objects of `obj_class` using `mapping`
        from raw `sql`
        """

        cur = self.cursor()
        ctx = {
                'table': mapping.db_table,
                }
        cur.execute(sql % ctx)

        res = cur.fetchall()

        for row in res:
            obj = obj_class()
            yield mapping.row_to_object(row, obj)

    def connect(self):
        self._connection = self._db.connect(**self._connection_opts)
        try:
            self._db.initialize_connection(self._connection)
        except AttributeError:
            pass
        return self._connection

    def is_connected(self):
        return self._connection is not None

    def close_connection(self):
        if self.is_connected():
            self._connection.close()
            self._connection = None

    @property
    def connection(self):
        return self._connection if self.is_connected() else self.connect()

    def init(self, **connection_opts):
        self._connection_opts = connection_opts

    def start_transaction(self):
        cur = self.cursor()
        cur.execute('begin')

    def commit_transaction(self):
        self.connection.commit()

    def rollback_transaction(self):
        self.connection.rollback()
