
class MappingError(Exception):
    pass


class ColumnNotDefined(MappingError):
    pass


class ColumnAlreadyMapped(MappingError):
    pass


class PropertyAlreadyMapped(MappingError):
    pass


class Mapping(object):
    def __init__(
            self, table, mapping=None, primary_key=None, scaffold=False):
        self._c2p = {}
        self._p2c = {}
        self._dc = []
        self._tablename = table
        self._pk = []
        self.scaffold = scaffold

        if mapping:
            for columnname, propname in mapping.items():
                self.add(columnname, propname)

        if primary_key:
            self.set_primary_key(primary_key)

    def add(self, column_name, property_name):
        if column_name in self._c2p:
            raise ColumnAlreadyMapped(column_name)

        if property_name in self._p2c:
            raise PropertyAlreadyMapped(column_name)

        self._c2p[column_name] = property_name
        self._p2c[property_name] = column_name

        if column_name not in self._pk:
            self._dc.append(column_name)

    def row_to_object(self, row, obj):
        for colname, propname in self._c2p.items():
            try:
                value = row[colname]
            except (IndexError, KeyError):
                value = None
            setattr(obj, propname, value)
        return obj

    def object_to_dict(self, obj):
        result = {}
        for propname, colname in self._p2c.items():
            try:
                result[colname] = getattr(obj, propname)
            except AttributeError:
                pass  # skip, won't be updated
        return result

    def columns(self):
        return self._c2p.keys()

    def data_columns(self):
        return self._dc[:]

    def primary_key(self):
        return self._pk[:]

    def set_primary_key(self, column_names):
        columns = self.columns()
        for column_name in column_names:
            if column_name not in columns:
                raise ColumnNotDefined(column_name)
        self._pk = column_names
        for column_name in self._pk:
            try:
                self._dc.remove(column_name)
            except ValueError:
                pass

    def properties(self):
        return self._p2c.keys()

    @property
    def db_table(self):
        return self._tablename


def scaffold(adapter, mapping):
    column_names = adapter._db.table_column_names(
            adapter, mapping.db_table)
    pk = adapter._db.table_primary_key(adapter, mapping.db_table)
    for name in column_names:
        mapping.add(name, name)
    mapping.set_primary_key(pk)
