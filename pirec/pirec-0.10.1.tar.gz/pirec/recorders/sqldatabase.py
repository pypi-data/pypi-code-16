"""Exposes the SQLDatabase result recorder."""
try:
    from sqlalchemy import create_engine, text
except ImportError:
    pass


class SQLDatabase(object):
    """Record results to a database supported by SQLAlchemy.

    Args:
        uri (str): database server URI e.g. ``mysql://username:password@localhost/dbname``
        table (str): table name
        values (dict): a mapping from database table columns to values

    See Also:
        `SQLAlchemy documentation <http://docs.sqlalchemy.org/en/latest/core/connections.html>`_
    """

    def __init__(self, uri, table, values):
        """Initialize the recorder."""
        self.uri = uri
        self.table = table
        self.values = values

    def write(self, results):
        """Write the results to the database table specified at initialisation.

        Args:
            results (dict): A dictionary of results to record
        """
        engine = create_engine(self.uri)
        field_names = ','.join(self.values.keys())
        values_placeholder = ','.join([':{0}'.format(k) for k in self.values.keys()])
        query_string = """
            INSERT INTO {table}
            ({field_names})
            VALUES ({values_placeholder})
        """
        query = text(query_string.format(
            table=self.table,
            field_names=field_names,
            values_placeholder=values_placeholder
        ))
        row = {}
        for field in self.values:
            row[field] = self.values[field](results)
        engine.execute(query, **row)
