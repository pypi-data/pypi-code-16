
class CSVAdapter(object):
    def __init__(self, db, **kwargs):
        self._connection_opts = kwargs
        self._connection = None
        self._db = db

    def select_all(self, mapping, obj_class):
        reader = self._db.reader(self.connection)
        for row in reader:
            obj = obj_class()
            yield mapping.row_to_object(row, obj)

    @property
    def connection(self):
        return self._connection if self._connection else self.connect()

    def connect(self):
        if not self._connection:
            self._connection = self._db.connect(**self._connection_opts)
        return self._connection

    def close_connection(self):
        if self._connection:
            self._connection.close()
            self._connection = None
